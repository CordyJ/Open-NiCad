// Generated using SwiftGen, by O.Halligon — https://github.com/SwiftGen/SwiftGen

#if os(OSX)
  import AppKit.NSColor
  internal typealias Color = NSColor
#elseif os(iOS) || os(tvOS) || os(watchOS)
  import UIKit.UIColor
  internal typealias Color = UIColor
#endif

// swiftlint:disable superfluous_disable_command
// swiftlint:disable file_length

// swiftlint:disable operator_usage_whitespace
internal extension Color {
  convenience init(rgbaValue: UInt32) {
    let red   = CGFloat((rgbaValue >> 24) & 0xff) / 255.0
    let green = CGFloat((rgbaValue >> 16) & 0xff) / 255.0
    let blue  = CGFloat((rgbaValue >>  8) & 0xff) / 255.0
    let alpha = CGFloat((rgbaValue      ) & 0xff) / 255.0

    self.init(red: red, green: green, blue: blue, alpha: alpha)
  }
}
// swiftlint:enable operator_usage_whitespace

// swiftlint:disable identifier_name line_length type_body_length
internal struct ColorName {
  internal let rgbaValue: UInt32
  internal var color: Color { return Color(named: self) }

  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#053866"></span>
  /// Alpha: 100% <br/> (0x053866ff)
  internal static let boltMobileBlueLabel = ColorName(rgbaValue: 0x053866ff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#001744"></span>
  /// Alpha: 100% <br/> (0x001744ff)
  internal static let boltMobileDarkBlue = ColorName(rgbaValue: 0x001744ff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#001644"></span>
  /// Alpha: 100% <br/> (0x001644ff)
  internal static let boltMobileGradientDark = ColorName(rgbaValue: 0x001644ff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#11a0d8"></span>
  /// Alpha: 100% <br/> (0x11a0d8ff)
  internal static let boltMobileGradientLight = ColorName(rgbaValue: 0x11a0d8ff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#eaeff2"></span>
  /// Alpha: 100% <br/> (0xeaeff2ff)
  internal static let boltMobileHomeBackgroundColour = ColorName(rgbaValue: 0xeaeff2ff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#001644"></span>
  /// Alpha: 100% <br/> (0x001644ff)
  internal static let boltMobileHomeButtonText = ColorName(rgbaValue: 0x001644ff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#e8e8e8"></span>
  /// Alpha: 100% <br/> (0xe8e8e8ff)
  internal static let boltMobileHomeGradientDark = ColorName(rgbaValue: 0xe8e8e8ff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#eaeff2"></span>
  /// Alpha: 100% <br/> (0xeaeff2ff)
  internal static let boltMobileHomeGradientLight = ColorName(rgbaValue: 0xeaeff2ff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#085386"></span>
  /// Alpha: 100% <br/> (0x085386ff)
  internal static let boltMobileHomeShadowColour = ColorName(rgbaValue: 0x085386ff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#11a0d8"></span>
  /// Alpha: 100% <br/> (0x11a0d8ff)
  internal static let boltMobileLightBlueLabel = ColorName(rgbaValue: 0x11a0d8ff)
}
// swiftlint:enable identifier_name line_length type_body_length

internal extension Color {
  convenience init(named color: ColorName) {
    self.init(rgbaValue: color.rgbaValue)
  }
}
