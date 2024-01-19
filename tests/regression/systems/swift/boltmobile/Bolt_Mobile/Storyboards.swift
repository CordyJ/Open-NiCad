// Generated using SwiftGen, by O.Halligon — https://github.com/SwiftGen/SwiftGen

// swiftlint:disable sorted_imports
import Foundation
import UIKit

// swiftlint:disable superfluous_disable_command
// swiftlint:disable file_length

internal protocol StoryboardType {
  static var storyboardName: String { get }
}

internal extension StoryboardType {
  static var storyboard: UIStoryboard {
    let name = self.storyboardName
    return UIStoryboard(name: name, bundle: Bundle(for: BundleToken.self))
  }
}

internal struct SceneType<T: Any> {
  internal let storyboard: StoryboardType.Type
  internal let identifier: String

  internal func instantiate() -> T {
    let identifier = self.identifier
    guard let controller = storyboard.storyboard.instantiateViewController(withIdentifier: identifier) as? T else {
      fatalError("ViewController '\(identifier)' is not of the expected class \(T.self).")
    }
    return controller
  }
}

internal struct InitialSceneType<T: Any> {
  internal let storyboard: StoryboardType.Type

  internal func instantiate() -> T {
    guard let controller = storyboard.storyboard.instantiateInitialViewController() as? T else {
      fatalError("ViewController is not of the expected class \(T.self).")
    }
    return controller
  }
}

internal protocol SegueType: RawRepresentable { }

internal extension UIViewController {
  func perform<S: SegueType>(segue: S, sender: Any? = nil) where S.RawValue == String {
    let identifier = segue.rawValue
    performSegue(withIdentifier: identifier, sender: sender)
  }
}

// swiftlint:disable explicit_type_interface identifier_name line_length type_body_length type_name
internal enum StoryboardScene {
  internal enum LaunchScreen: StoryboardType {
    internal static let storyboardName = "LaunchScreen"

    internal static let initialScene = InitialSceneType<UIViewController>(storyboard: LaunchScreen.self)
  }
  internal enum Main: StoryboardType {
    internal static let storyboardName = "Main"

    internal static let initialScene = InitialSceneType<UINavigationController>(storyboard: Main.self)

    internal static let askLocationVC = SceneType<Bolt_Mobile.AskLocationViewController>(storyboard: Main.self, identifier: "AskLocationVC")

    internal static let askExpertVC = SceneType<Bolt_Mobile.AskExpertViewController>(storyboard: Main.self, identifier: "askExpertVC")

    internal static let bookAppointmentVC = SceneType<Bolt_Mobile.BookAppointmentViewController>(storyboard: Main.self, identifier: "bookAppointmentVC")

    internal static let contactReviewDetailVC = SceneType<Bolt_Mobile.ContactReviewDetailViewController>(storyboard: Main.self, identifier: "contactReviewDetailVC")

    internal static let contactReviewVC = SceneType<Bolt_Mobile.ContactReviewViewController>(storyboard: Main.self, identifier: "contactReviewVC")

    internal static let couponDetailVC = SceneType<Bolt_Mobile.CouponDetailViewController>(storyboard: Main.self, identifier: "couponDetailVC")

    internal static let couponsVC = SceneType<Bolt_Mobile.CouponsViewController>(storyboard: Main.self, identifier: "couponsVC")

    internal static let deviceUpgradeVC = SceneType<Bolt_Mobile.DeviceUpgradeViewController>(storyboard: Main.self, identifier: "deviceUpgradeVC")

    internal static let homeVC = SceneType<Bolt_Mobile.HomeViewController>(storyboard: Main.self, identifier: "homeVC")

    internal static let welcomeVC = SceneType<Bolt_Mobile.WelcomeViewController>(storyboard: Main.self, identifier: "welcomeVC")
  }
  internal enum Referrals: StoryboardType {
    internal static let storyboardName = "Referrals"

    internal static let phoneNumberVerificationVC = SceneType<Bolt_Mobile.PhoneNumberVerificationViewController>(storyboard: Referrals.self, identifier: "phoneNumberVerificationVC")

    internal static let redeemCodeVC = SceneType<Bolt_Mobile.RedeemCodeViewController>(storyboard: Referrals.self, identifier: "redeemCodeVC")

    internal static let referralsContactVC = SceneType<Bolt_Mobile.ReferralsContactViewController>(storyboard: Referrals.self, identifier: "referralsContactVC")

    internal static let referralsInformationVC = SceneType<Bolt_Mobile.ReferralsInformationViewController>(storyboard: Referrals.self, identifier: "referralsInformationVC")

    internal static let referralsVC = SceneType<Bolt_Mobile.ReferralsViewController>(storyboard: Referrals.self, identifier: "referralsVC")
  }
}

internal enum StoryboardSegue {
}
// swiftlint:enable explicit_type_interface identifier_name line_length type_body_length type_name

private final class BundleToken {}
