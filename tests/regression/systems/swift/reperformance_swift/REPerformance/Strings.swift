// Generated using SwiftGen, by O.Halligon — https://github.com/SwiftGen/SwiftGen

import Foundation

// swiftlint:disable superfluous_disable_command
// swiftlint:disable file_length

// swiftlint:disable identifier_name line_length type_body_length
enum L10n {
  /// We sent you an email, please activate your account to log in.
  static let accountActivationMessage = L10n.tr("Localizable", "account_activation_message")
  /// Have you filled this out?
  static let basicProfileTestQuestion = L10n.tr("Localizable", "basic_profile_test_question")
  /// Bench Press
  static let benchPress = L10n.tr("Localizable", "bench_press")
  /// Camera
  static let camera = L10n.tr("Localizable", "camera")
  /// Would you like to enable permission to the camera?
  static let cameraPermission = L10n.tr("Localizable", "camera_permission")
  /// Cancel
  static let cancel = L10n.tr("Localizable", "cancel")
  /// Challenges
  static let challengeButtonTitle = L10n.tr("Localizable", "challenge_button_title")
  /// Details
  static let challengeDetailsTitle = L10n.tr("Localizable", "challenge_details_title")
  /// Challenge has ended
  static let challengeEnded = L10n.tr("Localizable", "challenge_ended")
  /// You cannot join a gym challenge when you do not belong to either gym.
  static let challengeGymChallengeJoinErrorMessage = L10n.tr("Localizable", "challenge_gym_challenge_join_error_message")
  /// Join alert
  static let challengeGymChallengeJoinErrorTitle = L10n.tr("Localizable", "challenge_gym_challenge_join_error_title")
  /// Gym Leaderboard
  static let challengeGymLeaderboardTitle = L10n.tr("Localizable", "challenge_gym_leaderboard_title")
  /// Join
  static let challengeJoin = L10n.tr("Localizable", "challenge_join")
  /// Joined
  static let challengeJoined = L10n.tr("Localizable", "challenge_joined")
  /// Get started in this challenge by visiting the test page, and test %@ at your %@ weight
  static func challengeJoinedMessage(_ p1: String, _ p2: String) -> String {
    return L10n.tr("Localizable", "challenge_joined_message", p1, p2)
  }
  /// Leaderboard
  static let challengeLeaderboardTitle = L10n.tr("Localizable", "challenge_leaderboard_title")
  /// Leave
  static let challengeLeave = L10n.tr("Localizable", "challenge_leave")
  /// Are you sure you want to leave this challenge?
  static let challengeLeavePromptMessage = L10n.tr("Localizable", "challenge_leave_prompt_message")
  /// Less then an hour left
  static let challengeLessThenHour = L10n.tr("Localizable", "challenge_less_then_hour")
  /// Starts in less than an hour
  static let challengeStartsInLessThanAnHour = L10n.tr("Localizable", "challenge_starts_in_less_than_an_hour")
  /// Challenges
  static let challengeTitle = L10n.tr("Localizable", "challenge_title")
  /// %@ joined
  static func challengeTotalJoined(_ p1: String) -> String {
    return L10n.tr("Localizable", "challenge_total_joined", p1)
  }
  /// Messages
  static let chatUsersTitle = L10n.tr("Localizable", "chat_users_title")
  /// Search
  static let chooseAGymSearchPlaceholder = L10n.tr("Localizable", "choose_a_gym_search_placeholder")
  /// Change your Gym
  static let chooseAGymTitleChange = L10n.tr("Localizable", "choose_a_gym_title_change")
  /// Find your Gym
  static let chooseAGymTitleFind = L10n.tr("Localizable", "choose_a_gym_title_find")
  /// Confirm
  static let confirm = L10n.tr("Localizable", "confirm")
  /// Credits available
  static let creditsAvailable = L10n.tr("Localizable", "credits_available")
  /// Cued Time
  static let cuedTime = L10n.tr("Localizable", "cued_time")
  /// DeadLift
  static let deadlift = L10n.tr("Localizable", "deadlift")
  /// Dollar Value
  static let dollarValue = L10n.tr("Localizable", "dollar_value")
  /// Done
  static let doneBarItemTitle = L10n.tr("Localizable", "done_bar_item_title")
  /// Email is not valid
  static let emailInvalid = L10n.tr("Localizable", "email_invalid")
  /// Email cannot be empty
  static let emailMissing = L10n.tr("Localizable", "email_missing")
  /// Endorsements
  static let endorsementsCellTitle = L10n.tr("Localizable", "endorsements_cell_title")
  /// Endurance
  static let endurance = L10n.tr("Localizable", "endurance")
  /// Error Getting Rewards
  static let errorGettingRewards = L10n.tr("Localizable", "error_getting_rewards")
  /// Error Loading Credits
  static let errorLoadingCredits = L10n.tr("Localizable", "error_loading_credits")
  /// Error Purchasing Reward
  static let errorPurchasingReward = L10n.tr("Localizable", "error_purchasing_reward")
  /// Error Redeeming Reward
  static let errorRedeemingReward = L10n.tr("Localizable", "error_redeeming_reward")
  /// Please report your score
  static let exerciseCardioInputInstructions = L10n.tr("Localizable", "exercise_cardio_input_instructions")
  /// Unable to retrieve exercise info, please try again.
  static let exerciseInfoErrorMessage = L10n.tr("Localizable", "exercise_info_error_message")
  /// Error Exercise Info
  static let exerciseInfoErrorTitle = L10n.tr("Localizable", "exercise_info_error_title")
  /// Track Running
  static let exerciseMileRunButton1Title = L10n.tr("Localizable", "exercise_mile_run_button1_title")
  /// Outdoor
  static let exerciseMileRunButton2Title = L10n.tr("Localizable", "exercise_mile_run_button2_title")
  /// Treadmill
  static let exerciseMileRunButton3Title = L10n.tr("Localizable", "exercise_mile_run_button3_title")
  /// Please report your score
  static let exerciseMileRunInputInstructions = L10n.tr("Localizable", "exercise_mile_run_input_instructions")
  /// Please pick your test format
  static let exerciseMileRunTestFormatInstructions = L10n.tr("Localizable", "exercise_mile_run_test_format_instructions")
  /// You must complete your profile before starting a test.
  static let exerciseProfileNotLoggedInDescription = L10n.tr("Localizable", "exercise_profile_not_logged_in_description")
  /// Stamina
  static let exerciseWeightLiftingButton1Title = L10n.tr("Localizable", "exercise_weight_lifting_button1_title")
  /// Endurance
  static let exerciseWeightLiftingButton2Title = L10n.tr("Localizable", "exercise_weight_lifting_button2_title")
  /// Strength
  static let exerciseWeightLiftingButton3Title = L10n.tr("Localizable", "exercise_weight_lifting_button3_title")
  /// Power
  static let exerciseWeightLiftingButton4Title = L10n.tr("Localizable", "exercise_weight_lifting_button4_title")
  /// Please enter total reps performed
  static let exerciseWeightLiftingInputInstructions = L10n.tr("Localizable", "exercise_weight_lifting_input_instructions")
  /// Here are your suggested testing weights
  static let exerciseWeightLiftingTestFormatInstructions = L10n.tr("Localizable", "exercise_weight_lifting_test_format_instructions")
  /// Self Timed
  static let exerciseYardDashButton1Title = L10n.tr("Localizable", "exercise_yard_dash_button1_title")
  /// Cued Time
  static let exerciseYardDashButton2Title = L10n.tr("Localizable", "exercise_yard_dash_button2_title")
  /// Timing yourself?
  static let exerciseYardDashTestFormatInstructionsOne = L10n.tr("Localizable", "exercise_yard_dash_test_format_instructions_one")
  /// Someone else timing you?
  static let exerciseYardDashTestFormatInstructionsTwo = L10n.tr("Localizable", "exercise_yard_dash_test_format_instructions_two")
  /// Exercises
  static let exercisesTitle = L10n.tr("Localizable", "exercises_title")
  /// First name cannot be empty
  static let firstNameMissing = L10n.tr("Localizable", "first_name_missing")
  /// Forty Yard Dash
  static let fortyYardDash = L10n.tr("Localizable", "forty_yard_dash")
  /// Gallery
  static let gallery = L10n.tr("Localizable", "gallery")
  /// Go to Settings
  static let goToSettings = L10n.tr("Localizable", "go_to_settings")
  /// See how you compare with other in your Gym
  static let gymLeaderboardInformationText = L10n.tr("Localizable", "gym_leaderboard_information_text")
  /// Gym Leaderboard
  static let gymLeaderboardTitle = L10n.tr("Localizable", "gym_leaderboard_title")
  /// Please ensure you enter units for your height (in or cm)
  static let heightCheckboxLeftBlank = L10n.tr("Localizable", "height_checkbox_left_blank")
  /// %d hrs ago
  static func hrsAgo(_ p1: Int) -> String {
    return L10n.tr("Localizable", "hrs ago", p1)
  }
  /// Would you like to enable permission to access the photo library?
  static let imagePermission = L10n.tr("Localizable", "image_permission")
  /// Choose Image Source
  static let imageSource = L10n.tr("Localizable", "image_source")
  /// Last name cannot be empty
  static let lastNameMissing = L10n.tr("Localizable", "last_name_missing")
  /// by all age groups
  static let leaderboardAllAgeGroupButtonTitle = L10n.tr("Localizable", "leaderboard_all_age_group_button_title")
  /// Unable to load leaderboard data
  static let leaderboardDefaultErrorMessage = L10n.tr("Localizable", "leaderboard_default_error_message")
  /// Your overall leaderboard is based on an average of all your submitted scores
  static let leaderboardFirstTimeView = L10n.tr("Localizable", "leaderboard_first_time_view")
  /// You must complete your profile before viewing leaderboards.
  static let leaderboardNotLoggedInDescription = L10n.tr("Localizable", "leaderboard_not_logged_in_description")
  /// Leaderboard
  static let leaderboardTabBarItemTitle = L10n.tr("Localizable", "leaderboard_tab_bar_item_title")
  /// Leaderboard
  static let leaderboardTitle = L10n.tr("Localizable", "leaderboard_title")
  /// by your age group
  static let leaderboardYourAgeGroupButtonTitle = L10n.tr("Localizable", "leaderboard_your_age_group_button_title")
  /// Compare with friends
  static let learnAboutProCompareWithFriends = L10n.tr("Localizable", "learn_about_pro_compare_with_friends")
  /// Who’s the best? See how you stack up against your Facebook friends, even in another city and country.
  static let learnAboutProCompareWithFriendsDetail = L10n.tr("Localizable", "learn_about_pro_compare_with_friends_detail")
  /// Exclusive deals
  static let learnAboutProExclusiveDeals = L10n.tr("Localizable", "learn_about_pro_exclusive_deals")
  /// Pro members have access to exclusive deals from our partners. Your credits go further with Pro too, since Pro members get discounts on deal purchases.\n\nREPerformance Pro Subscription:\n1-year subscription $49.99.  1-month subscription $4.99.\n\nPayment will be charged to iTunes Account at confirmation of purchase.\n\nSubscription automatically renews unless auto-renew is turned off at least 24-hours before the end of the current period.\n\nAccount will be charged for renewal within 24-hours prior to the end of the current period, and identify the cost of the renewal.\n\nSubscriptions may be managed by the user and auto-renewal may be turned off by going to the user's Account Settings after purchase\n\nAny unused portion of a free trial period, if offered, will be forfeited when the user purchases a subscription to that publication, where applicable
  static let learnAboutProExclusiveDealsDetail = L10n.tr("Localizable", "learn_about_pro_exclusive_deals_detail")
  /// Get
  static let learnAboutProGet = L10n.tr("Localizable", "learn_about_pro_get")
  /// Supercharge your performance with REPerformance Pro
  static let learnAboutProHeader = L10n.tr("Localizable", "learn_about_pro_header")
  /// Leaderboard
  static let learnAboutProLeaderboard = L10n.tr("Localizable", "learn_about_pro_leaderboard")
  /// See how you compare to others within your fitness category and within your city.
  static let learnAboutProLeaderboardDetail = L10n.tr("Localizable", "learn_about_pro_leaderboard_detail")
  /// Purchase is pending approval.
  static let learnAboutProPurchaseDeferred = L10n.tr("Localizable", "learn_about_pro_purchase_deferred")
  /// Restore Purchase
  static let learnAboutProRestorePurchase = L10n.tr("Localizable", "learn_about_pro_restore_purchase")
  /// Subscription expired.
  static let learnAboutProSubscriptionExpired = L10n.tr("Localizable", "learn_about_pro_subscription_expired")
  /// There are many various levels of fitness and a common mistake people often make is not fairly evaluating their own lifestyle and health efforts, when reflecting on their results.\n\nREPerformance has a solution. We identify what type of lifestyle you are currently in, then align you with others making the same commitments to health. This way you can compare, and track your current results to real people just like you.\n\nBeing part of the action group is having the awareness that fitness is important.  You are choosing to put your best foot forward and engage in healthy behaviors.\n\nBeing Action is taking action.\n\n
  static let lifestyleActionDetail = L10n.tr("Localizable", "lifestyle_action_detail")
  /// Action
  static let lifestyleActionTitle = L10n.tr("Localizable", "lifestyle_action_title")
  /// REPerformance understand your group. Living the lifestyle of an athlete is no small effort. Your group is bringing intensity and direction to every work out.\n\nNutrition is a tool for you, to increase your performance and bring your body closer and closer each day to optimum health. Being an Athlete is also having the awareness that performance comes from proper sleep and managing your outlook on life.\n\nREPerformance is a platform where you can access real tangible feedback to fulfill that competitiveness within you. We know you want to be the best you can be and have given you the place to do so.\n\nThere is no more guessing, your efforts equal your rank, train smart and train hard.\n\n
  static let lifestyleAthleteDetail = L10n.tr("Localizable", "lifestyle_athlete_detail")
  /// Athlete
  static let lifestyleAthleteTitle = L10n.tr("Localizable", "lifestyle_athlete_title")
  /// Hello Elite, and congratulations. Being here, training is a job, and lifestyle choices outside of the gym are rituals.\n\nYour group knows that the slight edge you are looking for with respect to performance markers is influenced by everything you do, you sleep right, you eat right and you think right, all for the common goal of reaching further with your fitness performance.\n\nREPerformance is your life, measure, compare and stack up against your peers and see who gets to the top of the leader board.\n\n
  static let lifestyleEliteDetail = L10n.tr("Localizable", "lifestyle_elite_detail")
  /// Elite
  static let lifestyleEliteTitle = L10n.tr("Localizable", "lifestyle_elite_title")
  /// Being "Fit" is commitment, and REPerformance knows that. We have carefully chosen our lifestyle markers so we can identify you, and provide you with a system where you can track analyze and compare your fitness results to Fit people like you.\n\nREPerformance recognizes that being fit is a lifestyle, where being active is now a routine and making healthy choices is part of your life.\n\nFit is a life, and your group is living it.\n\n
  static let lifestyleFitDetail = L10n.tr("Localizable", "lifestyle_fit_detail")
  /// Fit
  static let lifestyleFitTitle = L10n.tr("Localizable", "lifestyle_fit_title")
  /// Lifestyle
  static let lifestyleTitle = L10n.tr("Localizable", "lifestyle_title")
  /// Your lifestyle category is based on what you enter for your profile. You should update your profile to ensure you are in the correct lifestyle category.
  static let lifestyleTutorialSubtitle = L10n.tr("Localizable", "lifestyle_tutorial_subtitle")
  /// Lifestyle Tutorial
  static let lifestyleTutorialTitle = L10n.tr("Localizable", "lifestyle_tutorial_title")
  /// NHL Hockey Player
  static let marcusFolignoDescription = L10n.tr("Localizable", "marcus_foligno_description")
  /// Marcus Foligno
  static let marcusFolignoName = L10n.tr("Localizable", "marcus_foligno_name")
  /// Mile Run
  static let mileRun = L10n.tr("Localizable", "mile_run")
  /// Military Press
  static let militaryPress = L10n.tr("Localizable", "military_press")
  /// Missing Info
  static let missingInfo = L10n.tr("Localizable", "missing_info")
  /// My Best Scores
  static let myBestScoresTitle = L10n.tr("Localizable", "my_best_scores_title")
  /// My Latest Scores
  static let myLatestScoresTitle = L10n.tr("Localizable", "my_latest_scores_title")
  /// Name cannot exceed 30 characters.
  static let nameTooLong = L10n.tr("Localizable", "name_too_long")
  /// NHL Hockey Player
  static let nickFolignoDescription = L10n.tr("Localizable", "nick_foligno_description")
  /// Nick Foligno
  static let nickFolignoName = L10n.tr("Localizable", "nick_foligno_name")
  /// Please select your gym before trying to view the gym leaderboard.
  static let noGymSelectedMessage = L10n.tr("Localizable", "no_gym_selected_message")
  /// OK
  static let ok = L10n.tr("Localizable", "ok")
  /// REPerformance’s patent pending fitness normalization system, allows people from all ages and lifestyles to compare and compete fairly. Now, when you are comparing your results to others you are aligned with people that have a similar fitness level as you.
  static let ourValueAnswer1 = L10n.tr("Localizable", "our_value_answer_1")
  /// REP is, Relative Evaluation of Personal Performance. We have leveled the playing field by having the worlds first relative body weight comparison system. Gone are the days of who can 1 rep max the most, the new world is, how many Reps can you do. With our brand partners, we have given you access to exclusive deals. REP pays you to work out.
  static let ourValueAnswer2 = L10n.tr("Localizable", "our_value_answer_2")
  /// REPerformance was created out of the passion to have a real-world reflection of what fitness and health really is, no matter your goals or level of fitness. It is REP’s mantra to have no one left behind.
  static let ourValueAnswer3 = L10n.tr("Localizable", "our_value_answer_3")
  /// Rep is a tool you use to add intensity, focus and motivation to your existing training program. You can track, compare and compete in as many different exercises as you want. REP is your bench mark tool for your health so you know that you are always making progress.
  static let ourValueAnswer4 = L10n.tr("Localizable", "our_value_answer_4")
  /// REP pro members get discounts on the credit value of deals in our deal store. Pro members also get access to the leaderboards. Our leaderboards give pro members the ability to compete with the world, just their friends or just their region.
  static let ourValueAnswer5 = L10n.tr("Localizable", "our_value_answer_5")
  /// Why we are the leader in health and fitness measuring metrics?
  static let ourValueQuestion1 = L10n.tr("Localizable", "our_value_question_1")
  /// What makes us special?
  static let ourValueQuestion2 = L10n.tr("Localizable", "our_value_question_2")
  /// The general philosophy of REP.
  static let ourValueQuestion3 = L10n.tr("Localizable", "our_value_question_3")
  /// How should you use REP?
  static let ourValueQuestion4 = L10n.tr("Localizable", "our_value_question_4")
  /// What do I get for the subscription?
  static let ourValueQuestion5 = L10n.tr("Localizable", "our_value_question_5")
  /// Our Value
  static let ourValueTitle = L10n.tr("Localizable", "our_value_title")
  /// Outdoor
  static let outdoor = L10n.tr("Localizable", "outdoor")
  /// Password is not the same as Retype Passowrd
  static let passwordInvalid = L10n.tr("Localizable", "password_invalid")
  /// Password cannot be empty
  static let passwordMissing = L10n.tr("Localizable", "password_missing")
  /// Power
  static let power = L10n.tr("Localizable", "power")
  /// Profile
  static let profileNotLoggedInTitle = L10n.tr("Localizable", "profile_not_logged_in_title")
  /// You haven't updated your profile in over 90 days. Please take some time to update your profile.
  static let profileNotificationBody = L10n.tr("Localizable", "profile_notification_body")
  /// Profile
  static let profileTabBarItemTitle = L10n.tr("Localizable", "profile_tab_bar_item_title")
  /// Profile
  static let profileTitle = L10n.tr("Localizable", "profile_title")
  /// Rewards expire 30 days after purchasing, do you want to purchase this reward?
  static let purchaseAlertMessage = L10n.tr("Localizable", "purchase_alert_message")
  /// Purchase
  static let purchaseAlertTitle = L10n.tr("Localizable", "purchase_alert_title")
  /// Member of the Canadian National hockey team
  static let rebeccaJohnsonDescription = L10n.tr("Localizable", "rebecca_johnson_description")
  /// Rebecca Johnson
  static let rebeccaJohnsonName = L10n.tr("Localizable", "rebecca_johnson_name")
  /// Your report card is a comparison of your scores to other people in your demographic and lifestyle group
  static let reportCardFirstViewAlert = L10n.tr("Localizable", "report_card_first_view_alert")
  /// You must complete your profile before looking at your report card.
  static let reportCardNotLoggedInDescription = L10n.tr("Localizable", "report_card_not_logged_in_description")
  /// Report Card
  static let reportCardTabBarItemTitle = L10n.tr("Localizable", "report_card_tab_bar_item_title")
  /// Report Card
  static let reportCardTitle = L10n.tr("Localizable", "report_card_title")
  /// Please allow access to photos library in order to share on Instagram.
  static let requestUsePhotosLibrary = L10n.tr("Localizable", "request_use_photos_library")
  /// Please allow access to your photos library before sharing on Instagram. You can do this from the Settings App under REPerformance.
  static let requestUsePhotosLibraryDenied = L10n.tr("Localizable", "request_use_photos_library_denied")
  /// GET IT NOW
  static let rewardsGetItNow = L10n.tr("Localizable", "rewards_get_it_now")
  /// You must complete your profile before viewing rewards.
  static let rewardsNotLoggedInDescription = L10n.tr("Localizable", "rewards_not_logged_in_description")
  /// REDEEM
  static let rewardsRedeem = L10n.tr("Localizable", "rewards_redeem")
  /// Only redeem this deal when you are ready to pay for your order. The cashier is going to want to see this.
  static let rewardsRedeemInformation = L10n.tr("Localizable", "rewards_redeem_information")
  /// Rewards
  static let rewardsTabItemTitle = L10n.tr("Localizable", "rewards_tab_item_title")
  /// Exclusive Deals
  static let rewardsTitle = L10n.tr("Localizable", "rewards_title")
  /// Upgrade to Pro and access exclusive deals
  static let rewardsUpgradeToProDescription = L10n.tr("Localizable", "rewards_upgrade_to_pro_description")
  /// Upgrade to Pro
  static let rewardsUpgradeToProTitle = L10n.tr("Localizable", "rewards_upgrade_to_pro_title")
  /// Self Timed
  static let selfTimed = L10n.tr("Localizable", "self_timed")
  /// Check out my REPerformance report!
  static let shareReportFacebookInitialText = L10n.tr("Localizable", "share_report_facebook_initial_text")
  /// Sign Up
  static let signUpTitle = L10n.tr("Localizable", "sign_up_title")
  /// Squat
  static let squat = L10n.tr("Localizable", "squat")
  /// Stamina
  static let stamina = L10n.tr("Localizable", "stamina")
  /// Strength
  static let strength = L10n.tr("Localizable", "strength")
  /// The purpose of this test is to evaluate your upper body push capacity. Perform as many reps as possible with good form.
  static let testInformationBenchPressDescription = L10n.tr("Localizable", "test_information_bench_press_description")
  /// Way back in 1899 the man who invented the hack squat, named George Hackenschmidt rolled a 361-pound bar onto himself while laying on the floor and pressed it.
  static let testInformationBenchPressFunFact = L10n.tr("Localizable", "test_information_bench_press_fun_fact")
  /// Bench Press
  static let testInformationBenchPressTitle = L10n.tr("Localizable", "test_information_bench_press_title")
  /// The purpose of this test is to evaluate overall body strength. Complete as many reps as possible with good form.
  static let testInformationDeadliftDescription = L10n.tr("Localizable", "test_information_deadlift_description")
  /// The deadlift was popularized by Hermann Goerner in 1910. He recorded a 793 lbs two hand deadlift on October 29th, 1920.
  static let testInformationDeadliftFunFact = L10n.tr("Localizable", "test_information_deadlift_fun_fact")
  /// Deadlift
  static let testInformationDeadliftTitle = L10n.tr("Localizable", "test_information_deadlift_title")
  /// The purpose of this test is to evaluate your aerobic capacity.
  static let testInformationMileRunDescription = L10n.tr("Localizable", "test_information_mile_run_description")
  /// The test was designed by Kenneth H. Cooper in 1968 for US military use and was originally a 12-minute continuous run, with the distance traveled reflecting their absolute aerobic capacity. To make testing easier to administer Dr. Cooper made the alternative test a 1-mile run. This made the distance as a fixed and the finishing time measured.
  static let testInformationMileRunFunFact = L10n.tr("Localizable", "test_information_mile_run_fun_fact")
  /// Mile Run
  static let testInformationMileRunTitle = L10n.tr("Localizable", "test_information_mile_run_title")
  /// This test is performed to evaluate your overhead pressing muscle capacity.
  static let testInformationMilitaryPressDescription = L10n.tr("Localizable", "test_information_military_press_description")
  /// The overhead press is the oldest lift dating back to 6BC. The Greeks would etch their names in a stone after they lifted it overhead.
  static let testInformationMilitaryPressFunFact = L10n.tr("Localizable", "test_information_military_press_fun_fact")
  /// Military Press
  static let testInformationMilitaryPressTitle = L10n.tr("Localizable", "test_information_military_press_title")
  /// The purpose of this test is to evaluate your lower body muscle capacity.
  static let testInformationSquatDescription = L10n.tr("Localizable", "test_information_squat_description")
  /// The squat started as the deep knee bend. Lifters would use light weight for many reps at a time. This was done because there was no way to hoist heavy weight onto your back because the squat rack had not yet been invented.
  static let testInformationSquatFunFact = L10n.tr("Localizable", "test_information_squat_fun_fact")
  /// Squat
  static let testInformationSquatTitle = L10n.tr("Localizable", "test_information_squat_title")
  /// The purpose of the 40-yard dash or 36.5-meter sprint is to test your power, acceleration, and speed.
  static let testInformationYardDashDescription = L10n.tr("Localizable", "test_information_yard_dash_description")
  /// The origin of the 40 yards comes from the average distance of a punt and the time it takes to reach that distance.
  static let testInformationYardDashFunFact = L10n.tr("Localizable", "test_information_yard_dash_fun_fact")
  /// 40 Yard Dash
  static let testInformationYardDashTitle = L10n.tr("Localizable", "test_information_yard_dash_title")
  /// See how you compare with others based on your lifestyle category
  static let testLeaderboardInformationText = L10n.tr("Localizable", "test_leaderboard_information_text")
  /// Test Leaderboard
  static let testLeaderboardTitle = L10n.tr("Localizable", "test_leaderboard_title")
  /// Test
  static let testTabBarItemTitle = L10n.tr("Localizable", "test_tab_bar_item_title")
  /// Total Credits
  static let totalCredits = L10n.tr("Localizable", "total_credits")
  /// Track Running
  static let trackRunning = L10n.tr("Localizable", "track_running")
  /// Treadmill
  static let treadmill = L10n.tr("Localizable", "treadmill")
  /// We were unable to determine your location.
  static let unableDetermineLocationMessage = L10n.tr("Localizable", "unable_determine_location_message")
  /// Unable to share video
  static let unableToShareVideoMessage = L10n.tr("Localizable", "unable_to_share_video_message")
  /// Unknown Error
  static let unknownErrorMessage = L10n.tr("Localizable", "unknown_error_message")
  /// Missing User Gender
  static let userGenderMissingMessage = L10n.tr("Localizable", "user_gender_missing_message")
  /// Missing User Lifestyle
  static let userLifestyleMissingMessage = L10n.tr("Localizable", "user_lifestyle_missing_message")
  /// Missing User Token
  static let userTokenMissingMessage = L10n.tr("Localizable", "user_token_missing_message")
  /// Missing User Weight
  static let userWeightMissingMessage = L10n.tr("Localizable", "user_weight_missing_message")
  /// Validation
  static let validation = L10n.tr("Localizable", "validation")
  /// To keep REPerformance fair, you should verify your score by uploading a video clearly showing you earning that score.\n\nScores will be verified within 48 hours.
  static let videoVerificationInformationMessage = L10n.tr("Localizable", "video_verification_information_message")
  /// Ok
  static let videoVerificationInformationOkButtonTitle = L10n.tr("Localizable", "video_verification_information_ok_button_title")
  /// Verification
  static let videoVerificationInformationTitle = L10n.tr("Localizable", "video_verification_information_title")
  /// Warning
  static let warning = L10n.tr("Localizable", "warning")
  /// Please ensure you enter units for your weight (lbs or Kg)
  static let weightCheckboxLeftBlank = L10n.tr("Localizable", "weight_checkbox_left_blank")
  /// Your Deal
  static let yourDealTitle = L10n.tr("Localizable", "your_deal_title")
}
// swiftlint:enable identifier_name line_length type_body_length

extension L10n {
  private static func tr(_ table: String, _ key: String, _ args: CVarArg...) -> String {
    let format = NSLocalizedString(key, tableName: table, bundle: Bundle(for: BundleToken.self), comment: "")
    return String(format: format, locale: Locale.current, arguments: args)
  }
}

private final class BundleToken {}
