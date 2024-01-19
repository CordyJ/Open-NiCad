//
//  ReportCardDataProvider.swift
//  REPerformance
//
//  Created by Robert Kapizska on 2017-05-04.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Moya


class ReportCardDataProvider {
	
	let retrieveServiceProvider = MoyaProvider<RetrieveService>()
    let reportCardServiceProvider = MoyaProvider<ReportCardService>()
	
	func retrievePersonalReportCard(completion: @escaping ((ReportCard?, String?)->())) {
		guard let token = UserDefaults.standard.userToken else {
			completion(nil, L10n.userTokenMissingMessage)
			return
		}
		
		self.retrieveServiceProvider.request(.getPersonalReportCard(token: token)) { result in
			do {
				let response = try result.dematerialize()
				let reportCard = try response.map(ReportCard.self, atKeyPath: "data")
				completion(reportCard, nil)
			} catch {
				completion(nil, error.localizedDescription)
			}
		}
	}
	func retrieveAthleteReportCard(identifier: String, completion: @escaping ((ReportCard?, String?)->())) {
		guard let token = UserDefaults.standard.userToken else {
			completion(nil, L10n.userTokenMissingMessage)
			return
		}
		
		self.retrieveServiceProvider.request(.getAthleteReportCard(token: token, athlete: identifier)) { result in
			do {
				let response = try result.dematerialize()
				let reportCard = try response.map(ReportCard.self, atKeyPath: "data")
				completion(reportCard, nil)
			} catch {
				completion(nil, error.localizedDescription)
			}
		}
	}
	
	func retrieveScores(completion: @escaping (ReportCardExerciseScores?, String?)->()) {
		guard let token = UserDefaults.standard.userToken else {
			completion(nil, L10n.userTokenMissingMessage)
			return
		}
		
		self.retrieveServiceProvider.request(.getScores(token: token)) { result in
			do {
				let response = try result.dematerialize()
				let myScores = try response.map(ReportCardExerciseScores.self, atKeyPath: "data")
				completion(myScores, nil)
			} catch {
				completion(nil, error.localizedDescription)
			}
		}
	}
	
	func retrieveAthleteScores(identifier: String, completion: @escaping (ReportCardExerciseScores?, String?)->()) {
		guard let token = UserDefaults.standard.userToken else {
			completion(nil, L10n.userTokenMissingMessage)
			return
		}
		
		self.retrieveServiceProvider.request(.getAthleteScores(token: token, athlete: identifier)) { result in
			do {
				let response = try result.dematerialize()
				let myScores = try response.map(ReportCardExerciseScores.self, atKeyPath: "data")
				completion(myScores, nil)
			} catch {
				completion(nil, error.localizedDescription)
			}
		}
	}
	
	func updateProfileVisibility(isPrivate: Bool, completion: @escaping (String?)->()) {
		guard let token = UserDefaults.standard.userToken else {
			completion(L10n.userTokenMissingMessage)
			return
		}
		
		self.reportCardServiceProvider.request(.setProfilePrivacy(token: token, isPublic: !isPrivate)) { result in
			do {
				let response = try result.dematerialize()
				let _ = try response.map(REPerformanceBaseResponse<Bool>.self)
				completion(nil)
			} catch {
				completion(error.localizedDescription)
			}
		}
	}
    
    func updateProfileImage(completion: @escaping (String?)->()) {
        guard let token = UserDefaults.standard.userToken else {
            completion(L10n.userTokenMissingMessage)
            return
        }
        
        guard let profileImage = UIImage.getSavedProfileImage() else {
            completion("Missing profile image")
            return
        }
        
        self.reportCardServiceProvider.request(.setProfileImage(token: token, profileImage: profileImage)) { result in
            do {
                let response = try result.dematerialize()
                let _ = try response.map(REPerformanceBaseResponse<ProfileImage>.self)
                completion(nil)
            } catch {
                print(error.localizedDescription)
                completion(error.localizedDescription)
            }
        }
    }
    
    func getProfileImage(athleteID: Int, completion: @escaping (URL?)->()) {
        guard let token = UserDefaults.standard.userToken else {
            completion(nil)
            return
        }
        
        self.reportCardServiceProvider.request(.profileImage(token: token, athleteId: "\(athleteID)")) { result in
            do {
                let response = try result.dematerialize()
                let repResponse = try response.map(REPerformanceBaseResponse<ProfileImage>.self)
                completion(repResponse.data.image)
            } catch {
                print(error)
                completion(nil)
            }
        }
    }
}
