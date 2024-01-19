// Generated using SwiftGen, by O.Halligon — https://github.com/SwiftGen/SwiftGen

import Foundation

// swiftlint:disable superfluous_disable_command
// swiftlint:disable file_length

// swiftlint:disable identifier_name line_length type_body_length
internal enum L10n {
  /// No
  internal static let alertActionNoButtonTitle = L10n.tr("Localizable", "alert_action_no_button_title")
  /// OK
  internal static let alertActionOkButtonTitle = L10n.tr("Localizable", "alert_action_ok_button_title")
  /// Yes
  internal static let alertActionYesButtonTitle = L10n.tr("Localizable", "alert_action_yes_button_title")
  /// Back
  internal static let alertBackTitle = L10n.tr("Localizable", "alert_back_title")
  /// Try Again
  internal static let alertTryAgainTitle = L10n.tr("Localizable", "alert_try_again_title")
  /// ASK AN EXPERT
  internal static let askExpertTitle = L10n.tr("Localizable", "ask_expert_title")
  /// ATTRIDGE DRIVE
  internal static let attridgeTitle = L10n.tr("Localizable", "attridge_title")
  /// There was a problem getting your balance
  internal static let balanceDataMappingFailed = L10n.tr("Localizable", "balance_data_mapping_failed")
  /// BOOK APPOINTMENT
  internal static let bookAppointmentTitle = L10n.tr("Localizable", "book_appointment_title")
  /// Please use a device that is able to make phone calls
  internal static let callFailureMessage = L10n.tr("Localizable", "call_failure_message")
  /// CIRCLE DRIVE
  internal static let circleDriveTitle = L10n.tr("Localizable", "circle_drive_title")
  /// CHOOSE LOCATION
  internal static let contactReviewTitle = L10n.tr("Localizable", "contact_review_title")
  /// REDEEM
  internal static let couponDetailTitle = L10n.tr("Localizable", "coupon_detail_title")
  /// We are unable to show the details of this coupon
  internal static let couponErrorMessage = L10n.tr("Localizable", "coupon_error_message")
  /// Please make sure to redeem it in front of the cashier. Do you want to redeem it now?
  internal static let couponOneTimeUseDescription = L10n.tr("Localizable", "coupon_one_time_use_description")
  /// This coupon is one-time use only
  internal static let couponOneTimeUseTitle = L10n.tr("Localizable", "coupon_one_time_use_title")
  /// It must be redeemed by a Bolt Mobile sales associate
  internal static let couponWarningMessage = L10n.tr("Localizable", "coupon_warning_message")
  /// Are you sure you want to redeem this coupon?
  internal static let couponWarningTitle = L10n.tr("Localizable", "coupon_warning_title")
  /// COUPONS
  internal static let couponsTitle = L10n.tr("Localizable", "coupons_title")
  /// DEVICE UPGRADE
  internal static let deviceUpgradeTitle = L10n.tr("Localizable", "device_upgrade_title")
  /// 8TH STREET
  internal static let eightStreetTitle = L10n.tr("Localizable", "eight_street_title")
  /// Name: \nPhone Number: \n\nWhat can we help you with?\n
  internal static let emailBody = L10n.tr("Localizable", "email_body")
  /// Please set up email on your device in order to ask an expert
  internal static let emailFailureMessage = L10n.tr("Localizable", "email_failure_message")
  /// We were unable to send your message.
  internal static let emailNotSendMessage = L10n.tr("Localizable", "email_not_send_message")
  /// Your message has been sent, we will be in touch with you as soon as possible.
  internal static let emailSentMessage = L10n.tr("Localizable", "email_sent_message")
  /// Question for Expert
  internal static let emailSubject = L10n.tr("Localizable", "email_subject")
  /// Please connect to the internet
  internal static let internetNotReachableError = L10n.tr("Localizable", "internet_not_reachable_error")
  /// Please enter a valid email
  internal static let invalidEmail = L10n.tr("Localizable", "invalid_email")
  /// Invalid Entry
  internal static let invalidEntryTitle = L10n.tr("Localizable", "invalid_entry_title")
  /// Please enter a first name
  internal static let invalidFirstName = L10n.tr("Localizable", "invalid_first_name")
  /// Please enter a last name
  internal static let invalidLastName = L10n.tr("Localizable", "invalid_last_name")
  /// Please enter a valid 10 digit phone number
  internal static let invalidPhoneNumber = L10n.tr("Localizable", "invalid_phone_number")
  /// Name: \nPhone Number: \n\nWhat can we help you with?\n
  internal static let locationEmailBody = L10n.tr("Localizable", "location_email_body")
  /// Please set up email on your device iun order to email this location
  internal static let locationEmailFailureMessage = L10n.tr("Localizable", "location_email_failure_message")
  /// Email to Location
  internal static let locationEmailSubject = L10n.tr("Localizable", "location_email_subject")
  /// There was a problem logging in or updating your user information.
  internal static let loginUpdateDataMappingFailed = L10n.tr("Localizable", "login_update_data_mapping_failed")
  /// There was a problem redeeming.
  internal static let redeemDataMappingFailed = L10n.tr("Localizable", "redeem_data_mapping_failed")
  /// SEND
  internal static let referralButtonTitle = L10n.tr("Localizable", "referral_button_title")
  /// There was a problem submitting your referral
  internal static let referralDataMappingFailed = L10n.tr("Localizable", "referral_data_mapping_failed")
  /// EMAIL (OPTIONAL)
  internal static let referralEmailPlaceholder = L10n.tr("Localizable", "referral_email_placeholder")
  /// We were unable to send your referral becuase your information has not been entered. Go back to the referrals page to edit your info and then try again.
  internal static let referralErrorMessage = L10n.tr("Localizable", "referral_error_message")
  /// FIRST NAME
  internal static let referralFirstNamePlaceholder = L10n.tr("Localizable", "referral_first_name_placeholder")
  /// MY REFERRALS
  internal static let referralInformationTitle = L10n.tr("Localizable", "referral_information_title")
  /// LAST NAME
  internal static let referralLastNamePlaceholder = L10n.tr("Localizable", "referral_last_name_placeholder")
  /// CELL #
  internal static let referralPhoneNumberPlaceholder = L10n.tr("Localizable", "referral_phone_number_placeholder")
  /// Error Getting Code
  internal static let referralRedeemErrorGettingCode = L10n.tr("Localizable", "referral_redeem_error_getting_code")
  /// GIVE $25 GET $25
  internal static let referralRedeemTitle = L10n.tr("Localizable", "referral_redeem_title")
  /// I have a sweet deal for you! Save $25 when you buy your next phone at Bolt Mobile. Use my coupon code "%@" at any 4 Bolt Mobile locations in Saskatoon. See details at https://boltmobile.ca/refer
  internal static func referralSentMessageBody(_ p1: String) -> String {
    return L10n.tr("Localizable", "referral_sent_message_body", p1)
  }
  /// Thank you
  internal static let referralSentTitle = L10n.tr("Localizable", "referral_sent_title")
  /// WHO WOULD YOU LIKE TO GIVE $25 TO?
  internal static let referralsSubtitle = L10n.tr("Localizable", "referrals_subtitle")
  /// GIVE $25
  internal static let referralsTitle = L10n.tr("Localizable", "referrals_title")
  /// MY BOLT INFO
  internal static let referralsUserInformationTitle = L10n.tr("Localizable", "referrals_user_information_title")
  /// There was a problem decoding the response from the server
  internal static let requestFailedProblemDecoding = L10n.tr("Localizable", "request_failed_problem_decoding")
  /// ROSEWOOD
  internal static let rosewoodTitle = L10n.tr("Localizable", "rosewood_title")
  /// Please use a device that is able to send text messages
  internal static let textFailureMessage = L10n.tr("Localizable", "text_failure_message")
  /// We were unable to send your message.
  internal static let textNotSentMessage = L10n.tr("Localizable", "text_not_sent_message")
  /// Please check your messages to see your upgrade information.
  internal static let textSentMessage = L10n.tr("Localizable", "text_sent_message")
  /// Unable to load
  internal static let unableToLoadMessage = L10n.tr("Localizable", "unable_to_load_message")
  /// Unable to open website
  internal static let unableToOpenWebsite = L10n.tr("Localizable", "unable_to_open_website")
  /// UPGRADE
  internal static let upgradeMessageBody = L10n.tr("Localizable", "upgrade_message_body")
  /// Please enter a valid code
  internal static let verificationInvalidCodeMessage = L10n.tr("Localizable", "verification_invalid_code_message")
  /// There is an issue with your account. Please start the referrals process again.
  internal static let verificationInvalidUserMessage = L10n.tr("Localizable", "verification_invalid_user_message")
  /// We are unable to verify your phone number because we do not have an user token
  internal static let verificationMissingToken = L10n.tr("Localizable", "verification_missing_token")
  /// We were unable to resend your code
  internal static let verificationResendCodeFailureMessage = L10n.tr("Localizable", "verification_resend_code_failure_message")
  /// We sent your code again
  internal static let verificationResendCodeSuccessMessage = L10n.tr("Localizable", "verification_resend_code_success_message")
  /// VERIFICATION
  internal static let verificationTitle = L10n.tr("Localizable", "verification_title")
  /// STAY CONNECTED WITH US\nGET EXCLUSIVE DEALS\nAND EARN MONEY\nTO SPEND AT BOLT MOBILE
  internal static let welcomeText = L10n.tr("Localizable", "welcome_text")
  /// SUBMIT
  internal static let yourButtonTitle = L10n.tr("Localizable", "your_button_title")
  /// E-MAIL
  internal static let yourEmailPlaceholder = L10n.tr("Localizable", "your_email_placeholder")
  /// FIRST NAME
  internal static let yourFirstNamePlaceholder = L10n.tr("Localizable", "your_first_name_placeholder")
  /// LAST NAME
  internal static let yourLastNamePlaceholder = L10n.tr("Localizable", "your_last_name_placeholder")
  /// CELL #
  internal static let yourPhoneNumberPlaceholder = L10n.tr("Localizable", "your_phone_number_placeholder")
  /// To start earning Bolt Bucks we need your info
  internal static let yourUserInformationSubtitle = L10n.tr("Localizable", "your_user_information_subtitle")
}
// swiftlint:enable identifier_name line_length type_body_length

extension L10n {
  private static func tr(_ table: String, _ key: String, _ args: CVarArg...) -> String {
    let format = NSLocalizedString(key, tableName: table, bundle: Bundle(for: BundleToken.self), comment: "")
    return String(format: format, locale: Locale.current, arguments: args)
  }
}

private final class BundleToken {}
