// Phygital Memory's Keychain and Touch ID helper. The server runs it for what Python can't do safely: ask the person
// for their fingerprint (or Mac password), and keep secrets in the Keychain so only this helper can read them.
//
// Only Phygital Memory's own server may run it (checked below), and the Touch ID wording is fixed here, so another
// program can neither use it to read a secret nor show a Touch ID prompt with words of its own.
//
//   can                                 exit 0 when this Mac can ask (Touch ID, or the Mac password as fallback)
//   ask unlock|allow                    ask; exit 0 on yes
//   save <service> <account>            keep a memory's password for Touch ID unlock (secret on stdin)
//   get <service> <account>             ask ("unlock your memory"), then print that password
//   has <service> <account>             exit 0 when one is kept (reads nothing)
//   forget <service> <account>
//   keep <service> <account>            keep another secret (cloud password, GitHub key...), secret on stdin
//   read <service> <account>            print it (no prompt: the caller check is the guard)
//   drop <service> <account>
//   signer-new                          make a signing key inside this Mac's security chip (Secure Enclave), usable
//                                       only after Touch ID or the Mac password; print {"blob","public"} (the blob is
//                                       the chip's sealed handle: useless on any other Mac)
//   signer-sign <what>                  ask ("approve: <what>"), then sign; stdin: blob line, message line (base64);
//                                       print the signature (base64 DER). The server builds the words from the exact
//                                       approval it signs (Phygital Key format), and only the server may run this.
import CryptoKit
import Darwin
import Foundation
import LocalAuthentication
import Security

func fail(_ msg: String, _ code: Int32 = 1) -> Never {
    FileHandle.standardError.write((msg + "\n").data(using: .utf8)!)
    exit(code)
}

// The server sits two folders up from here: Resources/server/phygital-memory-server, with this helper at
// Resources/server/touchid/Phygital Memory. Its parent process must be exactly that program.
func callerIsOurServer() -> Bool {
    var buf = [CChar](repeating: 0, count: Int(MAXPATHLEN) * 4)
    guard proc_pidpath(getppid(), &buf, UInt32(buf.count)) > 0 else { return false }
    let parent = URL(fileURLWithPath: String(cString: buf)).resolvingSymlinksInPath().path
    let me = URL(fileURLWithPath: Bundle.main.executablePath ?? CommandLine.arguments[0]).resolvingSymlinksInPath()
    let server = me.deletingLastPathComponent().deletingLastPathComponent().appendingPathComponent("phygital-memory-server").path
    return parent == server
}

let REASONS = ["unlock": "unlock your memory", "allow": "let an AI app use your notes"]

func ask(_ kind: String) -> Bool {
    guard let reason = REASONS[kind] else { return false }
    let ctx = LAContext()
    var err: NSError?
    guard ctx.canEvaluatePolicy(.deviceOwnerAuthentication, error: &err) else { return false }
    let done = DispatchSemaphore(value: 0)
    var ok = false
    ctx.evaluatePolicy(.deviceOwnerAuthentication, localizedReason: reason) { yes, _ in ok = yes; done.signal() }
    done.wait()
    return ok
}

func query(_ service: String, _ account: String) -> [CFString: Any] {
    [kSecClass: kSecClassGenericPassword, kSecAttrService: service, kSecAttrAccount: account]
}

func store(_ service: String, _ account: String) {
    let secret = FileHandle.standardInput.readDataToEndOfFile()
    guard !secret.isEmpty else { fail("nothing to save", 2) }
    // Only this helper is trusted with the item: any other program (the `security` tool included) makes macOS ask
    // the person first.
    var me: SecTrustedApplication?
    var access: SecAccess?
    guard SecTrustedApplicationCreateFromPath(nil, &me) == errSecSuccess, let me,
          SecAccessCreate("Phygital Memory" as CFString, [me] as CFArray, &access) == errSecSuccess, let access
    else { fail("couldn't make the Keychain access rule") }
    SecItemDelete(query(service, account) as CFDictionary)
    var add = query(service, account)
    add[kSecValueData] = secret
    add[kSecAttrAccess] = access
    add[kSecAttrLabel] = service
    let s = SecItemAdd(add as CFDictionary, nil)
    if s != errSecSuccess { fail("Keychain said no (\(s))") }
}

func fetch(_ service: String, _ account: String) -> Never {
    var q = query(service, account)
    q[kSecReturnData] = true
    q[kSecMatchLimit] = kSecMatchLimitOne
    var out: CFTypeRef?
    let s = SecItemCopyMatching(q as CFDictionary, &out)
    guard s == errSecSuccess, let data = out as? Data else { fail("nothing kept (\(s))", 4) }
    FileHandle.standardOutput.write(data)
    exit(0)
}

let a = CommandLine.arguments
guard a.count >= 2 else { fail("usage: can | ask | save | get | has | forget | keep | read | drop", 2) }
guard callerIsOurServer() else { fail("only Phygital Memory may use this helper", 5) }
// every service it handles is the app's own
guard a.count < 3 || a[1] == "ask" || a[1] == "signer-sign" || a[2].hasPrefix("Phygital Memory") else { fail("not one of the app's items", 2) }

switch (a[1], a.count) {
case ("can", 2):
    exit(LAContext().canEvaluatePolicy(.deviceOwnerAuthentication, error: nil) ? 0 : 1)
case ("ask", 3):
    exit(ask(a[2]) ? 0 : 1)
case ("save", 4), ("keep", 4):
    store(a[2], a[3])
case ("get", 4):
    guard ask("unlock") else { fail("not confirmed", 3) }
    fetch(a[2], a[3])
case ("read", 4):
    fetch(a[2], a[3])
case ("has", 4):
    var q = query(a[2], a[3])
    q[kSecReturnAttributes] = true
    exit(SecItemCopyMatching(q as CFDictionary, nil) == errSecSuccess ? 0 : 1)
case ("forget", 4), ("drop", 4):
    let s = SecItemDelete(query(a[2], a[3]) as CFDictionary)
    exit(s == errSecSuccess || s == errSecItemNotFound ? 0 : 1)
case ("signer-new", 2):
    guard SecureEnclave.isAvailable else { fail("this Mac has no security chip", 6) }
    var cfErr: Unmanaged<CFError>?
    guard let access = SecAccessControlCreateWithFlags(nil, kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
                                                       [.privateKeyUsage, .userPresence], &cfErr)
    else { fail("couldn't make the access rule") }
    do {
        let key = try SecureEnclave.P256.Signing.PrivateKey(accessControl: access)
        let out = ["blob": key.dataRepresentation.base64EncodedString(),
                   "public": key.publicKey.derRepresentation.base64EncodedString()]
        FileHandle.standardOutput.write(try JSONSerialization.data(withJSONObject: out))
    } catch { fail("couldn't make the key: \(error)") }
case ("signer-sign", 3):
    let lines = String(decoding: FileHandle.standardInput.readDataToEndOfFile(), as: UTF8.self).split(separator: "\n")
    guard lines.count == 2, let blob = Data(base64Encoded: String(lines[0])), let msg = Data(base64Encoded: String(lines[1]))
    else { fail("give the key and the message", 2) }
    let ctx = LAContext()
    ctx.localizedReason = "approve: " + String(a[2].prefix(160))
    do {
        let key = try SecureEnclave.P256.Signing.PrivateKey(dataRepresentation: blob, authenticationContext: ctx)
        FileHandle.standardOutput.write(try key.signature(for: msg).derRepresentation.base64EncodedString().data(using: .utf8)!)
    } catch { fail("not signed: \(error)", 3) }
default:
    fail("usage: can | ask | save | get | has | forget | keep | read | drop | signer-new | signer-sign", 2)
}
