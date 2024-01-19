// Generated using SwiftGen, by O.Halligon — https://github.com/SwiftGen/SwiftGen

#if os(OSX)
  import AppKit.NSColor
  typealias Color = NSColor
#elseif os(iOS) || os(tvOS) || os(watchOS)
  import UIKit.UIColor
  typealias Color = UIColor
#endif

// swiftlint:disable superfluous_disable_command
// swiftlint:disable file_length

// swiftlint:disable operator_usage_whitespace
extension Color {
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
struct ColorName {
  let rgbaValue: UInt32
  var color: Color { return Color(named: self) }

  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#2850a3"></span>
  /// Alpha: 100% <br/> (0x2850a3ff)
  static let rePerformanceBlue = ColorName(rgbaValue: 0x2850a3ff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#2751a4"></span>
  /// Alpha: 100% <br/> (0x2751a4ff)
  static let rePerformanceBlueText = ColorName(rgbaValue: 0x2751a4ff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#1c99d6"></span>
  /// Alpha: 100% <br/> (0x1c99d6ff)
  static let rePerformanceNavGradientEnd = ColorName(rgbaValue: 0x1c99d6ff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#2374bd"></span>
  /// Alpha: 100% <br/> (0x2374bdff)
  static let rePerformanceNavGradientMiddle = ColorName(rgbaValue: 0x2374bdff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#294fa3"></span>
  /// Alpha: 100% <br/> (0x294fa3ff)
  static let rePerformanceNavGradientStart = ColorName(rgbaValue: 0x294fa3ff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#f5a623"></span>
  /// Alpha: 100% <br/> (0xf5a623ff)
  static let rePerformanceOrange = ColorName(rgbaValue: 0xf5a623ff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#3c4fa5"></span>
  /// Alpha: 100% <br/> (0x3c4fa5ff)
  static let rePerformanceRewardsBlue = ColorName(rgbaValue: 0x3c4fa5ff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#e3e3e3"></span>
  /// Alpha: 100% <br/> (0xe3e3e3ff)
  static let rePerformanceRewardsGrey = ColorName(rgbaValue: 0xe3e3e3ff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#e7a70c"></span>
  /// Alpha: 100% <br/> (0xe7a70cff)
  static let rePerformanceRewardsOrange = ColorName(rgbaValue: 0xe7a70cff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#ffffff"></span>
  /// Alpha: 100% <br/> (0xffffffff)
  static let rePerformanceWhite = ColorName(rgbaValue: 0xffffffff)
  /// <span style="display:block;width:3em;height:2em;border:1px solid black;background:#f5a623"></span>
  /// Alpha: 100% <br/> (0xf5a623ff)
  static let rePerformanceYellow = ColorName(rgbaValue: 0xf5a623ff)
}
// swiftlint:enable identifier_name line_length type_body_length

extension Color {
  convenience init(named color: ColorName) {
    self.init(rgbaValue: color.rgbaValue)
  }
}
