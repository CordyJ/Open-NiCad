// Generated using SwiftGen, by O.Halligon — https://github.com/SwiftGen/SwiftGen

#if os(OSX)
  import AppKit.NSImage
  typealias AssetColorTypeAlias = NSColor
  typealias Image = NSImage
#elseif os(iOS) || os(tvOS) || os(watchOS)
  import UIKit.UIImage
  typealias AssetColorTypeAlias = UIColor
  typealias Image = UIImage
#endif

// swiftlint:disable superfluous_disable_command
// swiftlint:disable file_length

@available(*, deprecated, renamed: "ImageAsset")
typealias AssetType = ImageAsset

struct ImageAsset {
  fileprivate var name: String

  var image: Image {
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

struct ColorAsset {
  fileprivate var name: String

  @available(iOS 11.0, tvOS 11.0, watchOS 4.0, OSX 10.13, *)
  var color: AssetColorTypeAlias {
    return AssetColorTypeAlias(asset: self)
  }
}

// swiftlint:disable identifier_name line_length nesting type_body_length type_name
enum Asset {
  enum Assets {
    static let background = ImageAsset(name: "Background")
    static let chatIcon = ImageAsset(name: "Chat Icon")
    static let checkGreen = ImageAsset(name: "Check_Green")
    static let checkYellow = ImageAsset(name: "Check_Yellow")
    static let circleX = ImageAsset(name: "Circle_X")
    static let disclosureIndicator = ImageAsset(name: "Disclosure Indicator")
    enum Endorsements {
      static let marcusFoligno = ImageAsset(name: "Marcus_Foligno")
      static let nickFoligno = ImageAsset(name: "Nick_Foligno")
      static let rebeccaJohnson = ImageAsset(name: "Rebecca_Johnson")
    }
    enum Exercises {
      enum ExerciseSelection {
        static let benchPress = ImageAsset(name: "benchPress")
        static let deadlift = ImageAsset(name: "deadlift")
        static let mileRun = ImageAsset(name: "mileRun")
        static let military = ImageAsset(name: "military")
        static let repLogo = ImageAsset(name: "repLogo")
        static let squat = ImageAsset(name: "squat")
        static let yardDash = ImageAsset(name: "yardDash")
      }
      static let activityLineBenchPress = ImageAsset(name: "activityLineBenchPress")
      static let activityLineDeadlift = ImageAsset(name: "activityLineDeadlift")
      static let activityLineMileRun = ImageAsset(name: "activityLineMileRun")
      static let activityLineMilitaryPress = ImageAsset(name: "activityLineMilitaryPress")
      static let activityLineSquat = ImageAsset(name: "activityLineSquat")
      static let activityLineYardDash = ImageAsset(name: "activityLineYardDash")
      static let benchPressBackground = ImageAsset(name: "benchPressBackground")
      static let deadliftBackground = ImageAsset(name: "deadliftBackground")
      static let medalWithFigure = ImageAsset(name: "medal-with-figure")
      static let medal = ImageAsset(name: "medal")
      static let mileRunBackground = ImageAsset(name: "mileRunBackground")
      static let militaryPressBackground = ImageAsset(name: "militaryPressBackground")
      static let profileNotCompleteBanner = ImageAsset(name: "profileNotCompleteBanner")
      static let squatBackground = ImageAsset(name: "squatBackground")
      static let yardDashBackground = ImageAsset(name: "yardDashBackground")
    }
    enum LifestyleTutorial {
      static let lifestyleAction = ImageAsset(name: "Lifestyle_Action")
      static let lifestyleActionBG = ImageAsset(name: "Lifestyle_Action_BG")
      static let lifestyleAthlete = ImageAsset(name: "Lifestyle_Athlete")
      static let lifestyleAthleteBG = ImageAsset(name: "Lifestyle_Athlete_BG")
      static let lifestyleElite = ImageAsset(name: "Lifestyle_Elite")
      static let lifestyleEliteBG = ImageAsset(name: "Lifestyle_Elite_BG")
      static let lifestyleFit = ImageAsset(name: "Lifestyle_Fit")
      static let lifestyleFitBG = ImageAsset(name: "Lifestyle_Fit_BG")
    }
    static let onboardingLogo = ImageAsset(name: "Onboarding_Logo")
    static let onboardingReport = ImageAsset(name: "Onboarding_Report")
    static let orangeDisclosureIndicatorRight = ImageAsset(name: "OrangeDisclosureIndicatorRight")
    static let orangeDisclosureIndicatorUp = ImageAsset(name: "OrangeDisclosureIndicatorUp")
    enum Profile {
      static let actionProfile = ImageAsset(name: "Action_Profile")
      static let athleteProfile = ImageAsset(name: "Athlete_Profile")
      static let eliteProfile = ImageAsset(name: "Elite_Profile")
      static let fitProfile = ImageAsset(name: "Fit_Profile")
      static let profileBasicInfo = ImageAsset(name: "Profile_Basic_Info")
      static let profileExercise = ImageAsset(name: "Profile_Exercise")
      static let profileLifeStyle = ImageAsset(name: "Profile_Life_style")
      static let profileNutrition = ImageAsset(name: "Profile_Nutrition")
      static let challengeIcon = ImageAsset(name: "challenge_icon")
      static let logoutIcon = ImageAsset(name: "logout_icon")
      static let loyaltyIcon = ImageAsset(name: "loyalty_icon")
      static let whiteCheckCircle = ImageAsset(name: "white_check_circle")
    }
    enum Rewards {
      static let whiteArrow = ImageAsset(name: "white-arrow")
    }
    enum TabBar {
      static let tabBarLeaderboard = ImageAsset(name: "TabBar_Leaderboard")
      static let tabBarProfile = ImageAsset(name: "TabBar_Profile")
      static let tabBarReportCard = ImageAsset(name: "TabBar_ReportCard")
      static let tabBarRewards = ImageAsset(name: "TabBar_Rewards")
      static let tabBarTests = ImageAsset(name: "TabBar_Tests")
    }
    static let torontoSkylineDELETE = ImageAsset(name: "TorontoSkyline_DELETE")
    enum VideoStatus {
      static let approveIcon = ImageAsset(name: "approve_icon")
      static let declinedIcon = ImageAsset(name: "declined_icon")
      static let novideoIcon = ImageAsset(name: "novideo_icon")
      static let reviewingIcon = ImageAsset(name: "reviewing_icon")
    }
    static let challengeBasicIcon = ImageAsset(name: "challenge-basic-icon")
    static let changeGymIcon = ImageAsset(name: "change-gym-icon")
    static let instagramIcon = ImageAsset(name: "instagram-icon")
    static let noVideoCamera = ImageAsset(name: "no-video-camera")
    static let nonFacebook = ImageAsset(name: "non-facebook")
    static let shareWhiteNoShadow = ImageAsset(name: "share-white-no-shadow")
    static let videoCamera = ImageAsset(name: "video-camera")
    static let xIcon = ImageAsset(name: "x-icon")

    // swiftlint:disable trailing_comma
    static let allColors: [ColorAsset] = [
    ]
    static let allImages: [ImageAsset] = [
      background,
      chatIcon,
      checkGreen,
      checkYellow,
      circleX,
      disclosureIndicator,
      Endorsements.marcusFoligno,
      Endorsements.nickFoligno,
      Endorsements.rebeccaJohnson,
      Exercises.ExerciseSelection.benchPress,
      Exercises.ExerciseSelection.deadlift,
      Exercises.ExerciseSelection.mileRun,
      Exercises.ExerciseSelection.military,
      Exercises.ExerciseSelection.repLogo,
      Exercises.ExerciseSelection.squat,
      Exercises.ExerciseSelection.yardDash,
      Exercises.activityLineBenchPress,
      Exercises.activityLineDeadlift,
      Exercises.activityLineMileRun,
      Exercises.activityLineMilitaryPress,
      Exercises.activityLineSquat,
      Exercises.activityLineYardDash,
      Exercises.benchPressBackground,
      Exercises.deadliftBackground,
      Exercises.medalWithFigure,
      Exercises.medal,
      Exercises.mileRunBackground,
      Exercises.militaryPressBackground,
      Exercises.profileNotCompleteBanner,
      Exercises.squatBackground,
      Exercises.yardDashBackground,
      LifestyleTutorial.lifestyleAction,
      LifestyleTutorial.lifestyleActionBG,
      LifestyleTutorial.lifestyleAthlete,
      LifestyleTutorial.lifestyleAthleteBG,
      LifestyleTutorial.lifestyleElite,
      LifestyleTutorial.lifestyleEliteBG,
      LifestyleTutorial.lifestyleFit,
      LifestyleTutorial.lifestyleFitBG,
      onboardingLogo,
      onboardingReport,
      orangeDisclosureIndicatorRight,
      orangeDisclosureIndicatorUp,
      Profile.actionProfile,
      Profile.athleteProfile,
      Profile.eliteProfile,
      Profile.fitProfile,
      Profile.profileBasicInfo,
      Profile.profileExercise,
      Profile.profileLifeStyle,
      Profile.profileNutrition,
      Profile.challengeIcon,
      Profile.logoutIcon,
      Profile.loyaltyIcon,
      Profile.whiteCheckCircle,
      Rewards.whiteArrow,
      TabBar.tabBarLeaderboard,
      TabBar.tabBarProfile,
      TabBar.tabBarReportCard,
      TabBar.tabBarRewards,
      TabBar.tabBarTests,
      torontoSkylineDELETE,
      VideoStatus.approveIcon,
      VideoStatus.declinedIcon,
      VideoStatus.novideoIcon,
      VideoStatus.reviewingIcon,
      challengeBasicIcon,
      changeGymIcon,
      instagramIcon,
      noVideoCamera,
      nonFacebook,
      shareWhiteNoShadow,
      videoCamera,
      xIcon,
    ]
    // swiftlint:enable trailing_comma
    @available(*, deprecated, renamed: "allImages")
    static let allValues: [AssetType] = allImages
  }
  enum ReportCard {
    static let profileImageUpdate = ImageAsset(name: "ProfileImageUpdate")
    static let reportCardAthleteFemale = ImageAsset(name: "ReportCardAthleteFemale")
    static let reportCardAthleteMale = ImageAsset(name: "ReportCardAthleteMale")
    static let reportCardLogo = ImageAsset(name: "ReportCardLogo")
    static let reportCardShareIcon = ImageAsset(name: "ReportCardShareIcon")
    static let scoreHeaderBenchPress = ImageAsset(name: "ScoreHeaderBenchPress")
    static let scoreHeaderDeadlift = ImageAsset(name: "ScoreHeaderDeadlift")
    static let scoreHeaderFortyYardDash = ImageAsset(name: "ScoreHeaderFortyYardDash")
    static let scoreHeaderMileRun = ImageAsset(name: "ScoreHeaderMileRun")
    static let scoreHeaderMilitaryPress = ImageAsset(name: "ScoreHeaderMilitaryPress")
    static let scoreHeaderSquat = ImageAsset(name: "ScoreHeaderSquat")

    // swiftlint:disable trailing_comma
    static let allColors: [ColorAsset] = [
    ]
    static let allImages: [ImageAsset] = [
      profileImageUpdate,
      reportCardAthleteFemale,
      reportCardAthleteMale,
      reportCardLogo,
      reportCardShareIcon,
      scoreHeaderBenchPress,
      scoreHeaderDeadlift,
      scoreHeaderFortyYardDash,
      scoreHeaderMileRun,
      scoreHeaderMilitaryPress,
      scoreHeaderSquat,
    ]
    // swiftlint:enable trailing_comma
    @available(*, deprecated, renamed: "allImages")
    static let allValues: [AssetType] = allImages
  }
}
// swiftlint:enable identifier_name line_length nesting type_body_length type_name

extension Image {
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

extension AssetColorTypeAlias {
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
