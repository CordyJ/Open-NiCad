// Generated using SwiftGen, by O.Halligon — https://github.com/SwiftGen/SwiftGen

#if os(OSX)
  import AppKit.NSImage
  internal typealias AssetColorTypeAlias = NSColor
  internal typealias Image = NSImage
#elseif os(iOS) || os(tvOS) || os(watchOS)
  import UIKit.UIImage
  internal typealias AssetColorTypeAlias = UIColor
  internal typealias Image = UIImage
#endif

// swiftlint:disable superfluous_disable_command
// swiftlint:disable file_length

@available(*, deprecated, renamed: "ImageAsset")
internal typealias AssetType = ImageAsset

internal struct ImageAsset {
  internal fileprivate(set) var name: String

  internal var image: Image {
    let bundle = Bundle(for: BundleToken.self)
    #if os(iOS) || os(tvOS)
    let image = Image(named: name, in: bundle, compatibleWith: nil)
    #elseif os(OSX)
    let image = bundle.image(forResource: NSImage.Name(name))
    #elseif os(watchOS)
    let image = Image(named: name)
    #endif
    guard let result = image else { fatalError("Unable to load image named \(name).") }
    return result
  }
}

internal struct ColorAsset {
  internal fileprivate(set) var name: String

  @available(iOS 11.0, tvOS 11.0, watchOS 4.0, OSX 10.13, *)
  internal var color: AssetColorTypeAlias {
    return AssetColorTypeAlias(asset: self)
  }
}

// swiftlint:disable identifier_name line_length nesting type_body_length type_name
internal enum Asset {
  internal enum Store {
    internal static let attridgeLocation = ImageAsset(name: "attridge-location")
    internal static let circleDriveLocation = ImageAsset(name: "circle-drive-location")
    internal static let clockIcon = ImageAsset(name: "clock-icon")
    internal static let eightStreetLocation = ImageAsset(name: "eight_street_location")
    internal static let facebookIcon = ImageAsset(name: "facebook-icon")
    internal static let googleIcon = ImageAsset(name: "google-icon")
    internal static let internetIcon = ImageAsset(name: "internet-icon")
    internal static let mailIcon = ImageAsset(name: "mail-icon")
    internal static let phoneIcon = ImageAsset(name: "phone-icon")
    internal static let pin = ImageAsset(name: "pin")
    internal static let tweedLaneLocation = ImageAsset(name: "tweed-lane-location")
  }
  internal static let askExpertIcon = ImageAsset(name: "ask_expert_icon")
  internal static let boltIcon = ImageAsset(name: "bolt_icon")
  internal static let boltLogo = ImageAsset(name: "bolt_logo")
  internal static let boltLogoDark = ImageAsset(name: "bolt_logo_dark")
  internal static let bookAppointmentIcon = ImageAsset(name: "book_appointment_icon")
  internal static let contactIcon = ImageAsset(name: "contact_icon")
  internal static let couponIcon = ImageAsset(name: "coupon_icon")
  internal static let deviceUpgradeIcon = ImageAsset(name: "device_upgrade_icon")
  internal static let home = ImageAsset(name: "home")
  internal static let infoBarButton = ImageAsset(name: "info_bar_button")
  internal static let referralsIcon = ImageAsset(name: "referrals_icon")
  internal static let sasktelLogo = ImageAsset(name: "sasktel_logo")
  internal static let xIcon = ImageAsset(name: "x_icon")

  // swiftlint:disable trailing_comma
  internal static let allColors: [ColorAsset] = [
  ]
  internal static let allImages: [ImageAsset] = [
    Store.attridgeLocation,
    Store.circleDriveLocation,
    Store.clockIcon,
    Store.eightStreetLocation,
    Store.facebookIcon,
    Store.googleIcon,
    Store.internetIcon,
    Store.mailIcon,
    Store.phoneIcon,
    Store.pin,
    Store.tweedLaneLocation,
    askExpertIcon,
    boltIcon,
    boltLogo,
    boltLogoDark,
    bookAppointmentIcon,
    contactIcon,
    couponIcon,
    deviceUpgradeIcon,
    home,
    infoBarButton,
    referralsIcon,
    sasktelLogo,
    xIcon,
  ]
  // swiftlint:enable trailing_comma
  @available(*, deprecated, renamed: "allImages")
  internal static let allValues: [AssetType] = allImages
}
// swiftlint:enable identifier_name line_length nesting type_body_length type_name

internal extension Image {
  @available(iOS 1.0, tvOS 1.0, watchOS 1.0, *)
  @available(OSX, deprecated,
    message: "This initializer is unsafe on macOS, please use the ImageAsset.image property")
  convenience init!(asset: ImageAsset) {
    #if os(iOS) || os(tvOS)
    let bundle = Bundle(for: BundleToken.self)
    self.init(named: asset.name, in: bundle, compatibleWith: nil)
    #elseif os(OSX)
    self.init(named: NSImage.Name(asset.name))
    #elseif os(watchOS)
    self.init(named: asset.name)
    #endif
  }
}

internal extension AssetColorTypeAlias {
  @available(iOS 11.0, tvOS 11.0, watchOS 4.0, OSX 10.13, *)
  convenience init!(asset: ColorAsset) {
    let bundle = Bundle(for: BundleToken.self)
    #if os(iOS) || os(tvOS)
    self.init(named: asset.name, in: bundle, compatibleWith: nil)
    #elseif os(OSX)
    self.init(named: NSColor.Name(asset.name), bundle: bundle)
    #elseif os(watchOS)
    self.init(named: asset.name)
    #endif
  }
}

private final class BundleToken {}
