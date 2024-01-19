//
//  ExercisesDataProvider.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-05-04.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import Moya

struct ExerciseResult {
    let submissionId: Int
    let totalRank: Int
    let rank: Int
    let creditsEarned:String
    let personalRecord:Bool
}

struct WeightResult {
    let stamina: Int
    let endurance: Int
    let strength: Int
    let power: Int
    
    func staminaWeightToDisplay() -> String {
        return "Stamina\n\(stamina) lbs"
    }

    func enduranceWeightToDisplay() -> String {
        return "Endurance\n\(endurance) lbs"
    }

    func strengthWeightToDisplay() -> String {
        return "Strength\n\(strength) lbs"
    }

    func powerWeightToDisplay() -> String {
        return "Power\n\(power) lbs"
    }

}

class ExercisesDataProvider {
    let retrieveProvider = MoyaProvider<RetrieveService>()
    let submitProvider = MoyaProvider<SubmitService>()
    
    func submitExercise(exercise:String, testFormat: String, score:Int, vimeoID: String?, completion:@escaping (ExerciseResult?, String?)->()) {
        guard let token = UserDefaults.standard.userToken else {
            completion(nil, L10n.userTokenMissingMessage)
            return
        }
        
        submitProvider.request(.submitExercise(token: token, exercise: exercise, testFormat: testFormat, score: score, vimeoID: vimeoID)) { result in
            do {
                let response = try result.dematerialize()
                let exerciseResult = try response.mapExerciseResult()
                completion(exerciseResult, nil)
            } catch {
                completion(nil, error.localizedDescription)
            }
        }
    }
    
    func submitVimeoId(vimeoId: String, submissionId: Int, completion:@escaping (Bool, String?) -> ()) {
        guard let token = UserDefaults.standard.userToken else {
            completion(false, L10n.userTokenMissingMessage)
            return
        }
    
        submitProvider.request(.submitCacheVimeo(token: token, vimeoID: vimeoId, submissionID: submissionId)) { result in
            do {
                let response = try result.dematerialize()
                let (success, errorMessage) = try response.mapCacheVimeo()
                if success {
                    completion(true, nil)
                } else {
                    completion(false, errorMessage)
                }
            } catch {
                completion(false, error.localizedDescription)
            }
        }
    }
    
    func retrieveWeight(exercise: ExerciseCategory, completion:@escaping (WeightResult?, String?) -> ()) {
        guard let token = UserDefaults.standard.userToken else {
            completion(nil, L10n.userTokenMissingMessage)
            return
        }
        
        guard let weight = UserDefaults.standard.userWeight else {
            completion(nil, L10n.userWeightMissingMessage)
            return
        }

        guard let gender = UserDefaults.standard.userGender else {
            completion(nil, L10n.userGenderMissingMessage)
            return
        }

        guard let lifestyle = UserDefaults.standard.lifestyleType else {
            completion(nil, L10n.userLifestyleMissingMessage)
            return
        }

        retrieveProvider.request(.getWeights(token: token, lifestyle: lifestyle, gender: gender, weight: weight, exercise: exercise)) { result in
            do {
                let response = try result.dematerialize()
                let weightResult = try response.mapWeightResult()
                completion(weightResult, nil)
            } catch {
                completion(nil, error.localizedDescription)
            }
        }
    }
}

extension Moya.Response {
    
    func mapExerciseResult() throws -> ExerciseResult {
        let responseObject = try self.map(to: REPerformanceResponse.self)
        
        guard responseObject.success else {
            throw REPerformanceError.requestFailed(responseObject.message)
        }
        
        guard let rankOutOf = responseObject.data["rank_out_of"]?.intValue,
            let rank = responseObject.data["rank"]?.intValue else {
                throw MoyaError.jsonMapping(self)
        }
        
        guard let creditsEarned = responseObject.data["credits"]?.stringValue else {
            throw MoyaError.jsonMapping(self)
        }
        
        guard let personalRecord = responseObject.data["personal_record"]?.boolValue else {
            throw MoyaError.jsonMapping(self)
        }
        
        guard let submissionId = responseObject.data["submission_id"]?.intValue else {
            throw MoyaError.jsonMapping(self)
        }
        
        return (ExerciseResult(submissionId: submissionId, totalRank: rankOutOf, rank: rank, creditsEarned: creditsEarned, personalRecord: personalRecord))
    }
 
    func mapCacheVimeo() throws -> (Bool, String?) {
        let responseObject = try self.map(to: REPerformanceResponse.self)
        
        guard responseObject.success else {
            throw REPerformanceError.requestFailed(responseObject.message)
        }
        return (true, nil)
    }

    func mapWeightResult() throws -> WeightResult {
        let responseObject = try self.map(to: REPerformanceResponse.self)
        
        guard responseObject.success else {
            throw REPerformanceError.requestFailed(responseObject.message)
        }

        guard let stamina = responseObject.data["stamina"]?.intValue else {
            throw MoyaError.jsonMapping(self)
        }

        guard let endurance = responseObject.data["endurance"]?.intValue else {
            throw MoyaError.jsonMapping(self)
        }

        guard let strength = responseObject.data["strength"]?.intValue else {
            throw MoyaError.jsonMapping(self)
        }

        guard let power = responseObject.data["power"]?.intValue else {
            throw MoyaError.jsonMapping(self)
        }

        return (WeightResult(stamina: stamina, endurance: endurance, strength: strength, power: power))
    }
}
