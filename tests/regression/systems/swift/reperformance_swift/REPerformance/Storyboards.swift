// Generated using SwiftGen, by O.Halligon — https://github.com/SwiftGen/SwiftGen

// swiftlint:disable sorted_imports
import Foundation
import UIKit

// swiftlint:disable superfluous_disable_command
// swiftlint:disable file_length

protocol StoryboardType {
  static var storyboardName: String { get }
}

extension StoryboardType {
  static var storyboard: UIStoryboard {
    let name = self.storyboardName
    return UIStoryboard(name: name, bundle: Bundle(for: BundleToken.self))
  }
}

struct SceneType<T: Any> {
  let storyboard: StoryboardType.Type
  let identifier: String

  func instantiate() -> T {
    let identifier = self.identifier
    guard let controller = storyboard.storyboard.instantiateViewController(withIdentifier: identifier) as? T else {
      fatalError("ViewController '\(identifier)' is not of the expected class \(T.self).")
    }
    return controller
  }
}

struct InitialSceneType<T: Any> {
  let storyboard: StoryboardType.Type

  func instantiate() -> T {
    guard let controller = storyboard.storyboard.instantiateInitialViewController() as? T else {
      fatalError("ViewController is not of the expected class \(T.self).")
    }
    return controller
  }
}

protocol SegueType: RawRepresentable { }

extension UIViewController {
  func perform<S: SegueType>(segue: S, sender: Any? = nil) where S.RawValue == String {
    let identifier = segue.rawValue
    performSegue(withIdentifier: identifier, sender: sender)
  }
}

// swiftlint:disable explicit_type_interface identifier_name line_length type_body_length type_name
enum StoryboardScene {
  enum Challenges: StoryboardType {
    static let storyboardName = "Challenges"

    static let challengeGymLeaderboardViewController = SceneType<REPerformance.ChallengeGymLeaderboardViewController>(storyboard: Challenges.self, identifier: "Challenge Gym Leaderboard View Controller")

    static let challengeDetailVC = SceneType<REPerformance.ChallengeDetailViewController>(storyboard: Challenges.self, identifier: "challengeDetailVC")

    static let challengeGymsVC = SceneType<REPerformance.ChallengeGymsViewController>(storyboard: Challenges.self, identifier: "challengeGymsVC")

    static let challengesVC = SceneType<REPerformance.ChallengesViewController>(storyboard: Challenges.self, identifier: "challengesVC")
  }
  enum Chat: StoryboardType {
    static let storyboardName = "Chat"

    static let chatMessagesViewController = SceneType<REPerformance.ChatMessagesViewController>(storyboard: Chat.self, identifier: "Chat Messages View Controller")

    static let chatUserListViewController = SceneType<REPerformance.ChatUserListViewController>(storyboard: Chat.self, identifier: "Chat User List View Controller")
  }
  enum Exercises: StoryboardType {
    static let storyboardName = "Exercises"

    static let exercisesVC = SceneType<REPerformance.ExercisesViewController>(storyboard: Exercises.self, identifier: "ExercisesVC")

    static let exerciseInformationVC = SceneType<REPerformance.ExercisesInformationViewController>(storyboard: Exercises.self, identifier: "exerciseInformationVC")

    static let exercisesFortyYardDashVC = SceneType<REPerformance.ExercisesReportFortyYardDashViewController>(storyboard: Exercises.self, identifier: "exercisesFortyYardDashVC")

    static let exercisesReportMileRunVC = SceneType<REPerformance.ExercisesReportMileRunViewController>(storyboard: Exercises.self, identifier: "exercisesReportMileRunVC")

    static let exercisesReportRepsVC = SceneType<REPerformance.ExercisesReportRepsViewController>(storyboard: Exercises.self, identifier: "exercisesReportRepsVC")

    static let exercisesStartVC = SceneType<REPerformance.ExercisesStartViewController>(storyboard: Exercises.self, identifier: "exercisesStartVC")

    static let exercisesSubmissionResultsVC = SceneType<REPerformance.ExercisesSubmissionResultsViewController>(storyboard: Exercises.self, identifier: "exercisesSubmissionResultsVC")
  }
  enum LaunchScreen: StoryboardType {
    static let storyboardName = "LaunchScreen"

    static let initialScene = InitialSceneType<UIViewController>(storyboard: LaunchScreen.self)
  }
  enum Leaderboard: StoryboardType {
    static let storyboardName = "Leaderboard"

    static let leaderboardSelectionVC = SceneType<REPerformance.LeaderboardSelectionViewController>(storyboard: Leaderboard.self, identifier: "LeaderboardSelectionVC")

    static let learnAboutProVC = SceneType<REPerformance.LearnAboutProViewController>(storyboard: Leaderboard.self, identifier: "LearnAboutProVC")

    static let attributionsVC = SceneType<REPerformance.AttributionsViewController>(storyboard: Leaderboard.self, identifier: "attributionsVC")

    static let chooseAGymVC = SceneType<REPerformance.ChooseAGymViewController>(storyboard: Leaderboard.self, identifier: "chooseAGymVC")

    static let gymLeaderboardVC = SceneType<REPerformance.GymLeaderboardViewController>(storyboard: Leaderboard.self, identifier: "gymLeaderboardVC")

    static let leaderboardInitialVC = SceneType<REPerformance.LeaderboardInitialViewController>(storyboard: Leaderboard.self, identifier: "leaderboardInitialVC")

    static let leaderboardVC = SceneType<REPerformance.LeaderboardViewController>(storyboard: Leaderboard.self, identifier: "leaderboardVC")

    static let mapSearchResultsTVC = SceneType<REPerformance.MapSearchResultsTableViewController>(storyboard: Leaderboard.self, identifier: "mapSearchResultsTVC")
  }
  enum Main: StoryboardType {
    static let storyboardName = "Main"

    static let initialScene = InitialSceneType<UINavigationController>(storyboard: Main.self)

    static let basicProfileVC = SceneType<REPerformance.BaseProfileViewController>(storyboard: Main.self, identifier: "BasicProfileVC")

    static let rePerformanceWarningVC = SceneType<REPerformance.REPerformanceWarningViewController>(storyboard: Main.self, identifier: "REPerformanceWarningVC")
  }
  enum Onboarding: StoryboardType {
    static let storyboardName = "Onboarding"

    static let initialScene = InitialSceneType<REPerformance.WelcomeViewController>(storyboard: Onboarding.self)

    static let lifestyleTutorialVC = SceneType<REPerformance.LifestyleTutorialViewController>(storyboard: Onboarding.self, identifier: "LifestyleTutorialVC")

    static let lifestyleVC = SceneType<REPerformance.LifestyleViewController>(storyboard: Onboarding.self, identifier: "LifestyleVC")

    static let signUpVC = SceneType<REPerformance.SignUpViewController>(storyboard: Onboarding.self, identifier: "SignUpVC")

    static let termsAndCondVC = SceneType<REPerformance.TermsAndConditionsViewController>(storyboard: Onboarding.self, identifier: "TermsAndCondVC")

    static let welcomeVC = SceneType<REPerformance.WelcomeViewController>(storyboard: Onboarding.self, identifier: "WelcomeVC")
  }
  enum OurValue: StoryboardType {
    static let storyboardName = "OurValue"

    static let endorsementsVC = SceneType<REPerformance.EndorsementsViewController>(storyboard: OurValue.self, identifier: "endorsementsVC")

    static let ourValueVC = SceneType<REPerformance.OurValueTableViewController>(storyboard: OurValue.self, identifier: "ourValueVC")
  }
  enum Profile: StoryboardType {
    static let storyboardName = "Profile"

    static let achievementsViewControllerStoryboardIdentifier = SceneType<REPerformance.AchievementsViewController>(storyboard: Profile.self, identifier: "Achievements View Controller Storyboard Identifier")

    static let profileVC = SceneType<REPerformance.ProfileViewController>(storyboard: Profile.self, identifier: "ProfileVC")

    static let basicInfoQuestionnaireVC = SceneType<REPerformance.BasicInfoProfileTableViewController>(storyboard: Profile.self, identifier: "basicInfoQuestionnaireVC")

    static let locationSearchVC = SceneType<REPerformance.LocationSearchTableViewController>(storyboard: Profile.self, identifier: "locationSearchVC")

    static let questionnaireVC = SceneType<REPerformance.BaseProfileViewController>(storyboard: Profile.self, identifier: "questionnaireVC")
  }
  enum ReportCard: StoryboardType {
    static let storyboardName = "ReportCard"

    static let myBestScoresViewControllerStoryboardIdentifier = SceneType<REPerformance.MyBestScoresViewController>(storyboard: ReportCard.self, identifier: "My Best Scores View Controller Storyboard Identifier")

    static let myScoresViewController = SceneType<REPerformance.MyScoresViewController>(storyboard: ReportCard.self, identifier: "MyScoresViewController")

    static let reportCardVC = SceneType<REPerformance.ReportCardViewController>(storyboard: ReportCard.self, identifier: "ReportCardVC")
  }
  enum Rewards: StoryboardType {
    static let storyboardName = "Rewards"

    static let redeemVC = SceneType<REPerformance.RedeemViewController>(storyboard: Rewards.self, identifier: "redeemVC")

    static let rewardsVC = SceneType<REPerformance.RewardsViewController>(storyboard: Rewards.self, identifier: "rewardsVC")

    static let yourDealVC = SceneType<REPerformance.YourDealViewController>(storyboard: Rewards.self, identifier: "yourDealVC")
  }
}

enum StoryboardSegue {
}
// swiftlint:enable explicit_type_interface identifier_name line_length type_body_length type_name

private final class BundleToken {}
