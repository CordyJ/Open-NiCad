//
//  REPerformanceAPIs.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-05-02.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Moya


#if USE_PRODUCTION
fileprivate let BaseURL = URL(string: "https://reperformance-live.appspot.com/api/v1")!
#else
fileprivate let BaseURL = URL(string: "https://reperformance-beta.appspot.com/api/v1")!
#endif


enum ExerciseCategory: String, Decodable {
	case MileRun = "mile_run"
	case FortyYardDash = "forty_yard_dash"
	case BenchPress = "bench_press"
	case DeadLift = "deadlift"
	case Squat = "squat"
	case MilitaryPress = "military_press"
	
	var readable: String {
		get {
			switch self {
			case .MileRun:
				return L10n.mileRun
			case .FortyYardDash:
				return L10n.fortyYardDash
			case .BenchPress:
				return L10n.benchPress
			case .DeadLift:
				return L10n.deadlift
			case .Squat:
				return L10n.squat
			case .MilitaryPress:
				return L10n.militaryPress
			}
		}
	}
}

enum ExerciseTestFormat: String {
	case TrackRunning = "track_running"
	case Outdoor = "outdoor"
	case Treadmill = "treadmill"
	case SelfTimed = "self_timed"
	case CuedTime = "cued_time"
	case Stamina = "stamina"
	case Endurance = "endurance"
	case Strength = "strength"
	case Power = "power"
}

enum LeaderboardGroup: String {
	case Everyone = "everyone"
	case Friends = "friends"
	case Nearby = "nearby"
	case Gym = "gym"
}

enum OnboardingService {
	case login(email: String, password: String)
	case createAccount(first: String, last: String, email: String, password: String)
	case signupWithFacebook(facebookID: String, facebookToken: String)
	case forgotPassword(email: String)
}

enum SubmitService {
	case submitProfile(token: String, lifestyle_category: LifestyleType, gender: String, weight: Int, age: Int, country_code: String, region_code: String)
	case submitExercise(token: String, exercise: String, testFormat: String, score: Int, vimeoID: String?)
	case purchaseReward(token: String, rewardID: String, proUser:Bool)
	case redeemReward(token: String, rewardID:String)
	case submitGym(token: String, placeID: String, name: String, region: String)
	case submitCacheVimeo(token: String, vimeoID: String, submissionID:Int)
	case submitChallengeJoin(token: String, challenge: Challenge)
	case submitChallengeLeave(token: String, challenge: Challenge)
}

enum RetrieveService {
	case conferenceMode()
	case getPersonalReportCard(token: String)
	case getAthleteReportCard(token: String, athlete: String)
	case getScores(token: String)
	case getAthleteScores(token: String, athlete: String)
	case getLeaderboard(token: String, group: LeaderboardGroup, filter_age: Bool, exercise: ExerciseCategory, test_format: ExerciseTestFormat)
	case getChallengeLeaderboard(challenge: Challenge, gym: Gym?)
	case getDefaultLeaderboard(token: String, group: LeaderboardGroup, filter_age: Bool)
	case getGymLeaderboard(token: String, exercise: ExerciseCategory, test_format: ExerciseTestFormat)
	case getCredits(token: String)
	case getRewards(token: String)
	case getChallenges(token: String)
	case getWeights(token:String, lifestyle: String, gender: String, weight: Int, exercise: ExerciseCategory)
}

enum AchievementsService {
	case getAchievements(token: String)
}

enum ReportCardService {
	case setProfilePrivacy(token: String, isPublic: Bool)
    case setProfileImage(token: String, profileImage: UIImage)
    case profileImage(token: String, athleteId: String)
}

enum NotificationService {
	case registerDevice(token: String, deviceToken: String)
	case unregisterDevice(token: String, deviceToken: String)
	case registerFirebaseToken(token: String, firebaseToken: String)
}

enum ChatService {
	case generateAuthToken(token: String)
}


//MARK: - Onboarding Service

extension OnboardingService: TargetType {
	
	var baseURL: URL {
		return BaseURL
	}
	
	var path: String {
		switch self {
		case .login, .signupWithFacebook:
			return "/login/"
		case .createAccount:
			return "/create-account/"
		case .forgotPassword:
			return "/reset-password/"
		}
	}
	var method: Moya.Method {
		switch self {
		case .login, .createAccount, .signupWithFacebook, .forgotPassword:
			return .get
		}
	}
	
	var sampleData: Data {
		switch self {
		case .login:
			return "{\"email\": \"edward.boone@pushinteractions.com\", \"password\": \"password\"}".data(using: String.Encoding.utf8)!
		case .createAccount:
			return "{\"first_name\": \"edward\", \"last_name\": \"boone\", \"email\": \"edward.boone@pushinteractions.com\", \"password\": \"password\"}".data(using: String.Encoding.utf8)!
		case .forgotPassword:
			return "{\"email\": \"edward.boone@pushinteractions.com\"}".data(using: String.Encoding.utf8)!
		default:
			return Data()
		}
	}
	
	var task: Task {
		switch self {
		case .login(let email, let password):
			return .requestParameters(parameters: ["email": email, "password": password], encoding: URLEncoding.default)
		case .createAccount(let first, let last, let email, let password):
			return .requestParameters(parameters: ["first_name": first, "last_name": last, "email": email, "password": password], encoding: URLEncoding.default)
		case .signupWithFacebook(let facebookID, let facebookToken):
			return .requestParameters(parameters: ["facebook_id": facebookID, "facebook_token": facebookToken], encoding: URLEncoding.default)
		case .forgotPassword(let email):
			return .requestParameters(parameters: ["email": email], encoding: URLEncoding.default)
		}
	}
	
	var headers: [String:String]? {
		switch self {
		case .login, .createAccount, .signupWithFacebook, .forgotPassword:
			return nil
		}
	}
}

//MARK: - Submit Service

extension SubmitService: TargetType {
	
	var baseURL: URL {
		return BaseURL
	}
	
	var path: String {
		switch self {
		case .submitProfile:
			return "/submit-profile/"
		case .submitExercise:
			return "/submit-exercise/"
		case .purchaseReward:
			return "/purchase-reward/"
		case .redeemReward:
			return "/redeem-reward/"
		case .submitGym:
			return "/submit-gym/"
		case .submitCacheVimeo:
			return "/submit-video/"
		case .submitChallengeJoin(_, let challenge):
			return "/challenges/\(challenge.uniqueIdentifier)/join/"
		case .submitChallengeLeave(_, let challenge):
			return "/challenges/\(challenge.uniqueIdentifier)/leave/"
		}
	}
	var method: Moya.Method {
		switch self {
		case .submitProfile, .submitExercise, .purchaseReward, .redeemReward, .submitGym, .submitCacheVimeo, .submitChallengeJoin, .submitChallengeLeave:
			return .post
		}
	}
	
	var sampleData: Data {
		switch self {
		case .submitProfile:
			return "{\"token\": \"faketoken\", \"lifestyle_category\": \"lifestyle_category\", \"age\": \"age\", \"country_code\": \"country_code\", \"region_code\":\"region_code\"}".data(using: String.Encoding.utf8)!
		case .submitExercise:
			return "{\"token\": \"faketoken\", \"exercise\": \"exercise\", \"test_format\": \"test_format\", \"score\": \"score\"}".data(using: String.Encoding.utf8)!
		case .purchaseReward:
			return "{\"token\": \"faketoken\", \"reward_id\": \"1\", \"proUser\":\"true\"}".data(using: String.Encoding.utf8)!
		case .redeemReward:
			return "{\"token\": \"faketoken\", \"reward_id\": \"1\"}".data(using: String.Encoding.utf8)!
		case .submitGym:
			return "{\"token\": \"faketoken\", \"place_id\": \"placeid\", \"name\": \"testGym\", \"region\": \"testRegion\",}".data(using: String.Encoding.utf8)!
		case .submitCacheVimeo:
			return "{\"token\": \"faketoken\", \"vimeo_id\": \"0\", \"submission_id\": \"0\"}".data(using: String.Encoding.utf8)!
		case .submitChallengeJoin, .submitChallengeLeave:
			return "{\"token\": \"faketoken\"}".data(using: String.Encoding.utf8)!
		}
	}
	
	var task: Task {
		switch self {
		case .submitProfile(let token, let lifestyleCategory, let gender, let weight, let age, let countryCode, let regionCode):
			var parameters = [String : Any]()
			parameters["token"] = token
			parameters["lifestyle_category"] = lifestyleCategory.rawValue.lowercased()
			parameters["gender"] = gender.lowercased()
			parameters["weight"] = weight
			parameters["age"] = age
			parameters["country_code"] = countryCode
			parameters["region_code"] = regionCode
			
			return .requestParameters(parameters: parameters, encoding: JSONEncoding.default)
		case .submitExercise(let token, let exercise, let testFormat, let score, let vimeoID):
			if let vimeoID = vimeoID {
				return .requestParameters(parameters: ["token": token, "exercise": exercise, "test_format": testFormat, "score": score, "vimeo_id": vimeoID], encoding: JSONEncoding.default)
			} else {
				return .requestParameters(parameters: ["token": token, "exercise": exercise, "test_format": testFormat, "score": score], encoding: JSONEncoding.default)
			}
		case .purchaseReward(let token, let rewardID, let proUser):
			return .requestParameters(parameters: ["token": token, "reward_id":rewardID, "pro_user":proUser], encoding: JSONEncoding.default)
		case .redeemReward(let token, let rewardID):
			return .requestParameters(parameters: ["token": token, "reward_id":rewardID], encoding: JSONEncoding.default)
		case .submitGym(let token, let placeID, let name, let region):
			return .requestParameters(parameters: ["token": token, "place_id": placeID, "name": name, "region": region], encoding: JSONEncoding.default)
		case .submitCacheVimeo(let token, let vimeoID, let submissionID):
			return .requestParameters(parameters: ["token": token, "vimeo_id":vimeoID, "submission_id":submissionID], encoding: JSONEncoding.default)
		case .submitChallengeJoin(let token, _), .submitChallengeLeave(let token, _):
			return .requestParameters(parameters: ["token": token], encoding: JSONEncoding.default)
		}
	}
	
	var headers: [String:String]? {
		switch self {
		case .submitProfile, .submitExercise, .purchaseReward, .redeemReward, .submitGym, .submitCacheVimeo, .submitChallengeJoin, .submitChallengeLeave:
			return nil
		}
	}
}

//MARK: - Retrieve Service

extension RetrieveService: TargetType {
	
	var baseURL: URL {
		return BaseURL
	}
	
	var path: String {
		switch self {
		case .conferenceMode:
			return "/get-conference-mode/"
		case .getPersonalReportCard:
			return "/report-card/"
		case .getAthleteReportCard(_, let identifier):
			return "/report-card/\(identifier)/"
		case .getScores:
			return "/scores/"
		case .getAthleteScores(_, let identifier):
			return "/scores/\(identifier)/"
		case .getLeaderboard, .getDefaultLeaderboard, .getGymLeaderboard:
			return "/leader-board/"
		case .getCredits:
			return "/get-credits/"
		case .getRewards:
			return "/get-rewards/"
		case .getChallenges:
			return "/challenges/"
		case .getChallengeLeaderboard(let challenge, _):
			return "/challenges/\(challenge.uniqueIdentifier)/leaderboard/"
		case .getWeights:
			return "/exercise-weights/"
		}
	}
	var method: Moya.Method {
		switch self {
		case .conferenceMode, .getPersonalReportCard, .getAthleteReportCard, .getScores, .getAthleteScores, .getLeaderboard, .getDefaultLeaderboard, .getGymLeaderboard, .getCredits, .getRewards, .getChallenges, .getChallengeLeaderboard, .getWeights:
			return .get
		}
	}
	
	var sampleData: Data {
		switch self {
		case .conferenceMode:
			return "{\"message\": \"Conference mode\", \"data\": {\"conference_mode_on\" : false}, \"success\": 1}".data(using: String.Encoding.utf8)!
		case .getPersonalReportCard, .getAthleteReportCard, .getScores, .getAthleteScores, .getCredits, .getRewards, .getChallenges:
			return "{\"token\": \"faketoken\"}".data(using: String.Encoding.utf8)!
		case .getLeaderboard:
			return "{\"token\": \"faketoken\", \"group\": \"group\", \"filter_age\": \"filter_age\", \"exercise\": \"exercise\", \"test_format\": \"test_format\"}".data(using: String.Encoding.utf8)!
		case .getDefaultLeaderboard:
			return "{\"token\": \"faketoken\", \"group\": \"group\", \"filter_age\": \"filter_age\"}".data(using: String.Encoding.utf8)!
		case .getGymLeaderboard:
			return "{\"token\": \"faketoken\", \"exercise\": \"exercise\", \"test_format\": \"test_format\"}".data(using: String.Encoding.utf8)!
		case .getWeights:
			return "{\"token\": \"faketoken\", \"exercise\": \"exercise\", \"lifestyle_category\": \"test_lifestyle_category\", \"gender\": \"female\", \"weight\": \"0\"}".data(using: String.Encoding.utf8)!
		default:
			return Data()
		}
	}
	
	var task: Task {
		switch self {
		case .conferenceMode:
			return .requestPlain
		case .getPersonalReportCard(let token), .getAthleteReportCard(let token, _), .getScores(let token), .getAthleteScores(let token, _), .getCredits(let token), .getRewards(let token), .getChallenges(let token):
			return .requestParameters(parameters: ["token": token], encoding: URLEncoding.default)
		case .getLeaderboard(let token, let group, let filter_age, let exercise, let test_format):
			return .requestParameters(parameters: ["token": token, "group":group.rawValue, "filter_age":filter_age, "exercise":exercise.rawValue, "test_format":test_format.rawValue], encoding: URLEncoding.default)
		case .getDefaultLeaderboard(let token, let group, let filter_age):
			return .requestParameters(parameters: ["token": token, "group":group.rawValue, "filter_age":filter_age], encoding: URLEncoding.default)
		case .getGymLeaderboard(let token, let exercise, let test_format):
			return .requestParameters(parameters: ["token": token, "group":"gym", "filter_age":false, "exercise":exercise.rawValue, "test_format":test_format.rawValue], encoding: URLEncoding.default)
		case .getChallengeLeaderboard(_, let gym):
			var parameters: [String : Any] = [:]
			
			if let gym = gym {
				parameters["gym_id"] = gym.id
			}
			
			return .requestParameters(parameters: parameters, encoding: URLEncoding.default)
		case .getWeights(let token, let lifestyleCategory, let gender, let weight,let exercise):
			return .requestParameters(parameters: ["token": token, "lifestyle_category": lifestyleCategory.lowercased(), "gender": gender.lowercased(), "weight": weight, "exercise":exercise.rawValue], encoding: URLEncoding.default)
		}
	}
	
	var headers: [String:String]? {
		switch self {
		case .conferenceMode, .getPersonalReportCard, .getAthleteReportCard, .getScores, .getAthleteScores, .getCredits, .getRewards, .getLeaderboard, .getDefaultLeaderboard, .getGymLeaderboard, .getChallenges, .getChallengeLeaderboard, .getWeights:
			return nil
		}
	}
}

//MARK: - Achievements Service

extension AchievementsService: TargetType {
	
	var baseURL: URL {
		return BaseURL
	}
	
	var path: String {
		switch self {
		case .getAchievements:
			return "/get-achievements/"
		}
	}
	
	var method: Moya.Method {
		switch self {
		case .getAchievements:
			return .get
		}
	}
	
	var sampleData: Data {
		switch self {
		case .getAchievements:
			let squatJSON = ["personal_best" : 100, "video" : 10, "submission" : 200] as [String : Any]
			let benchPressJSON = ["personal_best" : 100, "video" : 10, "submission" : 200] as [String : Any]
			let militaryPressJSON = ["personal_best" : 100, "video" : 10, "submission" : 200] as [String : Any]
			let fortyYardDashJSON = ["personal_best" : 100, "video" : 10, "submission" : 200] as [String : Any]
			let deadliftJSON = ["personal_best" : 100, "video" : 10, "submission" : 200] as [String : Any]
			let mileRunJSON = ["personal_best" : 100, "video" : 10, "submission" : 200] as [String : Any]
			let dataJson = ["squat" : squatJSON, "bench_press" : benchPressJSON, "military_press" : militaryPressJSON, "forty_yard_dash" : fortyYardDashJSON, "deadlift" : deadliftJSON, "mile_run" : mileRunJSON] as [String : Any]
			let json = ["message" : "Achievements", "data" : dataJson, "success" : 1] as [String : Any]
			let jsonText = try! JSONSerialization.data(withJSONObject: json, options: .prettyPrinted)
			
			return jsonText
		}
	}
	
	var task:Task {
		switch self {
		case .getAchievements(let token):
			return .requestParameters(parameters: ["token": token], encoding: URLEncoding.default)
		}
	}
	
	var headers: [String : String]? {
		switch self{
		case .getAchievements:
			return nil
		}
	}
}

//MARK: - Report Card Service

extension ReportCardService: TargetType {
	
	var baseURL: URL {
		return BaseURL
	}
	
	var path: String {
		switch self {
		case .setProfilePrivacy:
			return "/report-card/visibility/"
        case .setProfileImage:
            return "/submit-profile-image/"
        case .profileImage(_, let athleteId):
            return "profile-image/\(athleteId)/"
		}
	}
	
	var method: Moya.Method {
		switch self {
		case .setProfilePrivacy, .setProfileImage:
			return .post
        case .profileImage:
            return .get
		}
        
        
	}
	
	var sampleData: Data {
		return Data()
	}
	
	var task: Task {
		switch self {
		case .setProfilePrivacy(let token, let isPublic):
			return .requestParameters(parameters: ["token" : token, "public" : isPublic], encoding: URLEncoding.default)
        case .setProfileImage(let token, let profileImage):
            let parameters = ["token": token]
            let profileImageMultipartFormData = MultipartFormData(provider: .data(profileImage.jpegData(compressionQuality: 0.7)!), name: "image", fileName: "photo.jpg", mimeType: "image/jpeg")
                return .uploadCompositeMultipart([profileImageMultipartFormData], urlParameters: parameters)
        case .profileImage(let token, _):
            return .requestParameters(parameters: ["token": token], encoding: URLEncoding.default)
		}
	}
	
	var headers: [String : String]? {
		switch self {
		case .setProfilePrivacy:
			return nil
        case .setProfileImage:
            return nil
        case .profileImage:
            return nil
		}
	}
}

//MARK: - Notification Service

extension NotificationService: TargetType {
	
	var baseURL: URL {
		return BaseURL
	}
	
	var path: String {
		switch self {
		case .registerDevice:
			return "/register_notifications/"
		case .unregisterDevice:
			return "/unregister_notifications/"
		case .registerFirebaseToken:
			return "/register_ios_firebase_token/"
		}
	}
	
	var method: Moya.Method {
		switch self {
		case .registerDevice, .unregisterDevice, .registerFirebaseToken:
			return .post
		}
	}
	
	var sampleData: Data {
		return Data()
	}
	
	var task: Task {
		switch self {
		case .registerDevice(let token, let deviceToken), .unregisterDevice(let token, let deviceToken):
			return .requestParameters(parameters: ["token": token, "device_token" : deviceToken, "device_type" : 1], encoding: URLEncoding.default)
		case .registerFirebaseToken(let token, let firebaseToken):
			var parameters = [String : Any]()
			parameters["token"] = token
			parameters["firebase_ios_token"] = firebaseToken
			return .requestParameters(parameters: parameters, encoding: URLEncoding.default)
		}
	}
	
	var headers: [String : String]? {
		return nil
	}
}


extension ChatService: TargetType {
	
	var baseURL: URL {
		return BaseURL
	}
	
	var path: String {
		switch self {
		case .generateAuthToken:
			return "/auth-token/"
		}
	}
	
	var method: Moya.Method {
		switch self {
		case .generateAuthToken:
			return .get
		}
	}
	
	var sampleData: Data {
		return Data()
	}
	
	var task: Task {
		switch self {
		case .generateAuthToken(let token):
			return .requestParameters(parameters: ["token": token], encoding: URLEncoding.default)
		}
	}
	
	var headers: [String : String]? {
		return nil
	}
}


//MARK: - Response Handlers

extension Moya.Response {
	
	func mapSuccess() throws -> Bool {
		let responseObject = try self.map(to: REPerformanceResponse.self)
		
		if responseObject.success {
			return true
		}
		else {
			throw REPerformanceError.requestFailed(responseObject.message)
		}
	}
}
