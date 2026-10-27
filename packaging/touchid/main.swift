// Phygital Memory's Touch ID helper. The server runs it for the one thing Python can't do: ask the person for
// their fingerprint (or Mac password), and keep a memory's password in the Keychain so only this helper can read it.
//
//   can                              exit 0 when this Mac can ask (Touch ID, or the Mac password as fallback)
//   ask <reason>                     ask; exit 0 on yes
//   save <service> <account>         keep the secret given on stdin (only this helper may read it back)
//   get <service> <account> <reason> ask, then print the secret
//   has <service> <account>          exit 0 when a secret is kept (reads nothing)
//   forget <service> <account>
import Foundation
import LocalAuthentication
import Security

func fail(_ msg: String, _ code: Int32 = 1) -> Never {
    FileHandle.standardError.write((msg + "\n").data(using: .utf8)!)
    exit(code)
}

func ask(_ reason: String) -> Bool {
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

let a = CommandLine.arguments
guard a.count >= 2 else { fail("usage: can | ask | save | get | has | forget", 2) }

switch (a[1], a.count) {
case ("can", 2):
    exit(LAContext().canEvaluatePolicy(.deviceOwnerAuthentication, error: nil) ? 0 : 1)
case ("ask", 3):
    exit(ask(a[2]) ? 0 : 1)
case ("save", 4):
    let secret = FileHandle.standardInput.readDataToEndOfFile()
    guard !secret.isEmpty else { fail("nothing to save", 2) }
    // Only this helper is trusted with the item: any other program (the `security` tool included) makes macOS ask
    // the person first.
    var me: SecTrustedApplication?
    var access: SecAccess?
    guard SecTrustedApplicationCreateFromPath(nil, &me) == errSecSuccess, let me,
          SecAccessCreate("Phygital Memory" as CFString, [me] as CFArray, &access) == errSecSuccess, let access
    else { fail("couldn't make the Keychain access rule") }
    SecItemDelete(query(a[2], a[3]) as CFDictionary)
    var add = query(a[2], a[3])
    add[kSecValueData] = secret
    add[kSecAttrAccess] = access
    add[kSecAttrLabel] = a[2]
    let s = SecItemAdd(add as CFDictionary, nil)
    if s != errSecSuccess { fail("Keychain said no (\(s))") }
case ("get", 5):
    guard ask(a[4]) else { fail("not confirmed", 3) }
    var q = query(a[2], a[3])
    q[kSecReturnData] = true
    q[kSecMatchLimit] = kSecMatchLimitOne
    var out: CFTypeRef?
    let s = SecItemCopyMatching(q as CFDictionary, &out)
    guard s == errSecSuccess, let data = out as? Data else { fail("nothing kept (\(s))", 4) }
    FileHandle.standardOutput.write(data)
case ("has", 4):
    var q = query(a[2], a[3])
    q[kSecReturnAttributes] = true
    exit(SecItemCopyMatching(q as CFDictionary, nil) == errSecSuccess ? 0 : 1)
case ("forget", 4):
    let s = SecItemDelete(query(a[2], a[3]) as CFDictionary)
    exit(s == errSecSuccess || s == errSecItemNotFound ? 0 : 1)
default:
    fail("usage: can | ask | save | get | has | forget", 2)
}
