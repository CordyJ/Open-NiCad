//
//  ReportCardExerciseScores.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-08-06.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import Foundation


struct ReportCardExerciseScores: Decodable {
	
	private enum CodingKeys: String, CodingKey {
		case squat = "squat"
		case mileRun = "mile_run"
		case militaryPress = "military_press"
		case fortyYardDash = "forty_yard_dash"
		case deadlift = "deadlift"
		case benchPress = "bench_press"
	}
	
	
	var squat: ReportCardExerciseWeightScores
	var mileRun: ReportCardExerciseMileRunScores
	var militaryPress: ReportCardExerciseWeightScores
	var fortyYardDash: ReportCardExerciseFortyYardDashScores
	var deadlift: ReportCardExerciseWeightScores
	var benchPress: ReportCardExerciseWeightScores
	
	
	init(from decoder: Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.squat = try container.decode(ReportCardExerciseWeightScores.self, forKey: .squat)
		self.mileRun = try container.decode(ReportCardExerciseMileRunScores.self, forKey: .mileRun)
		self.militaryPress = try container.decode(ReportCardExerciseWeightScores.self, forKey: .militaryPress)
		self.fortyYardDash = try container.decode(ReportCardExerciseFortyYardDashScores.self, forKey: .fortyYardDash)
		self.deadlift = try container.decode(ReportCardExerciseWeightScores.self, forKey: .deadlift)
		self.benchPress = try container.decode(ReportCardExerciseWeightScores.self, forKey: .benchPress)
	}
}


struct ReportCardExerciseScore: Decodable {
	
	private enum CodingKeys: String, CodingKey {
		case date = "date"
		case volume = "volume"
		case score = "score"
		case video = "video"
		case weight = "weight"
	}
	
	
	var date: Date?
	var volume: Double?
	var score: Int?
	var video: VideoStatus
	var weight: Double?
	
	
	init(from decoder: Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.volume = try? container.decode(Double.self, forKey: .volume)
		self.score = try? container.decode(Int.self, forKey: .score)
		self.weight = try? container.decode(Double.self, forKey: .weight)
		
		if let dateString = try? container.decode(String.self, forKey: .date) {
			self.date = DateFormatter.serverDateFormatter().date(from: dateString)
		}
		
		if let video = try? container.decode(String.self, forKey: .video), let videoStatus = VideoStatus(rawValue: video) {
			self.video = videoStatus
		}
		else {
			self.video = .NoVideo
		}
	}
}


struct ReportCardExerciseMileRunScores: Decodable {
	
	private enum CodingKeys: String, CodingKey {
		case trackRunning = "track_running"
		case outdoor = "outdoor"
		case treadmill = "treadmill"
	}
	
	
	var trackRunning: ReportCardExerciseScore
	var outdoor: ReportCardExerciseScore
	var treadmill: ReportCardExerciseScore
	
	
	init(from decoder: Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.trackRunning = try container.decode(ReportCardExerciseScore.self, forKey: .trackRunning)
		self.outdoor = try container.decode(ReportCardExerciseScore.self, forKey: .outdoor)
		self.treadmill = try container.decode(ReportCardExerciseScore.self, forKey: .treadmill)
	}
}


struct ReportCardExerciseFortyYardDashScores: Decodable {
	
	private enum CodingKeys: String, CodingKey {
		case selfTimed = "self_timed"
		case cuedTime = "cued_time"
	}
	
	
	var selfTimed: ReportCardExerciseScore
	var cuedTime: ReportCardExerciseScore
	
	
	init(from decoder: Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.selfTimed = try container.decode(ReportCardExerciseScore.self, forKey: .selfTimed)
		self.cuedTime = try container.decode(ReportCardExerciseScore.self, forKey: .cuedTime)
	}
}


struct ReportCardExerciseWeightScores: Decodable {
	
	private enum CodingKeys: String, CodingKey {
		case stamina = "stamina"
		case endurance = "endurance"
		case strength = "strength"
		case power = "power"
	}
	
	
	var stamina: ReportCardExerciseScore
	var endurance: ReportCardExerciseScore
	var strength: ReportCardExerciseScore
	var power: ReportCardExerciseScore
	
	
	init(from decoder: Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.stamina = try container.decode(ReportCardExerciseScore.self, forKey: .stamina)
		self.endurance = try container.decode(ReportCardExerciseScore.self, forKey: .endurance)
		self.strength = try container.decode(ReportCardExerciseScore.self, forKey: .strength)
		self.power = try container.decode(ReportCardExerciseScore.self, forKey: .power)
	}
}


enum VideoStatus: String {
	case Reviewing = "reviewing"
	case Approved = "approved"
	case Declined = "declined"
	case NoVideo = "novideo"
}


extension ReportCardExerciseScores {
	
	func generateExerciseScoresViewModel() -> [(ExerciseInfo, [ExerciseScoreAthleteCellViewModel])] {
		let exerciseScores = self
		
		var viewModel = [(ExerciseInfo, [ExerciseScoreAthleteCellViewModel])]()
		let dateFormatter = DateFormatter.displayScoreResultsDateFormatter()
		
		let benchPress = ExerciseInfo(image: Asset.ReportCard.scoreHeaderBenchPress.image, title: "Bench Press", isWeightLifting: true)
		var benchPressScores = [ExerciseScoreAthleteCellViewModel]()
		benchPressScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Stamina", dateDisplay: (exerciseScores.benchPress.stamina.date != nil ? dateFormatter.string(from: exerciseScores.benchPress.stamina.date!) : nil), scoreDisplay: (exerciseScores.benchPress.stamina.score != nil ? "\(exerciseScores.benchPress.stamina.score!)" : nil), weight: exerciseScores.benchPress.stamina.weight, volume: exerciseScores.benchPress.stamina.volume))
		benchPressScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Endurance", dateDisplay: (exerciseScores.benchPress.endurance.date != nil ? dateFormatter.string(from: exerciseScores.benchPress.endurance.date!) : nil), scoreDisplay: (exerciseScores.benchPress.endurance.score != nil ? "\(exerciseScores.benchPress.endurance.score!)" : nil), weight: exerciseScores.benchPress.endurance.weight, volume: exerciseScores.benchPress.endurance.volume))
		benchPressScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Strength", dateDisplay: (exerciseScores.benchPress.strength.date != nil ? dateFormatter.string(from: exerciseScores.benchPress.strength.date!) : nil), scoreDisplay: (exerciseScores.benchPress.strength.score != nil ? "\(exerciseScores.benchPress.strength.score!)" : nil), weight: exerciseScores.benchPress.strength.weight, volume: exerciseScores.benchPress.strength.volume))
		benchPressScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Power", dateDisplay: (exerciseScores.benchPress.power.date != nil ? dateFormatter.string(from: exerciseScores.benchPress.power.date!) : nil), scoreDisplay: (exerciseScores.benchPress.power.score != nil ? "\(exerciseScores.benchPress.power.score!)" : nil), weight: exerciseScores.benchPress.power.weight, volume: exerciseScores.benchPress.power.volume))
		viewModel.append((benchPress, benchPressScores))
		
		let deadlift = ExerciseInfo(image: Asset.ReportCard.scoreHeaderDeadlift.image, title: "Deadlift", isWeightLifting: true)
		var deadliftScores = [ExerciseScoreAthleteCellViewModel]()
		deadliftScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Stamina", dateDisplay: (exerciseScores.deadlift.stamina.date != nil ? dateFormatter.string(from: exerciseScores.deadlift.stamina.date!) : nil), scoreDisplay: (exerciseScores.deadlift.stamina.score != nil ? "\(exerciseScores.deadlift.stamina.score!)" : nil), weight: exerciseScores.deadlift.stamina.weight, volume: exerciseScores.deadlift.stamina.volume))
		deadliftScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Endurance", dateDisplay: (exerciseScores.deadlift.endurance.date != nil ? dateFormatter.string(from: exerciseScores.deadlift.endurance.date!) : nil), scoreDisplay: (exerciseScores.deadlift.endurance.score != nil ? "\(exerciseScores.deadlift.endurance.score!)" : nil), weight: exerciseScores.deadlift.endurance.weight, volume: exerciseScores.deadlift.endurance.volume))
		deadliftScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Strength", dateDisplay: (exerciseScores.deadlift.strength.date != nil ? dateFormatter.string(from: exerciseScores.deadlift.strength.date!) : nil), scoreDisplay: (exerciseScores.deadlift.strength.score != nil ? "\(exerciseScores.deadlift.strength.score!)" : nil), weight: exerciseScores.deadlift.strength.weight, volume: exerciseScores.deadlift.strength.volume))
		deadliftScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Power", dateDisplay: (exerciseScores.deadlift.power.date != nil ? dateFormatter.string(from: exerciseScores.deadlift.power.date!) : nil), scoreDisplay: (exerciseScores.deadlift.power.score != nil ? "\(exerciseScores.deadlift.power.score!)" : nil), weight: exerciseScores.deadlift.power.weight, volume: exerciseScores.deadlift.power.volume))
		viewModel.append((deadlift, deadliftScores))
		
		let squat = ExerciseInfo(image: Asset.ReportCard.scoreHeaderSquat.image, title: "Squat", isWeightLifting: true)
		var squatScores = [ExerciseScoreAthleteCellViewModel]()
		squatScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Stamina", dateDisplay: (exerciseScores.squat.stamina.date != nil ? dateFormatter.string(from: exerciseScores.squat.stamina.date!) : nil), scoreDisplay: (exerciseScores.squat.stamina.score != nil ? "\(exerciseScores.squat.stamina.score!)" : nil), weight: exerciseScores.squat.stamina.weight, volume: exerciseScores.squat.stamina.volume))
		squatScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Endurance", dateDisplay: (exerciseScores.squat.endurance.date != nil ? dateFormatter.string(from: exerciseScores.squat.endurance.date!) : nil), scoreDisplay: (exerciseScores.squat.endurance.score != nil ? "\(exerciseScores.squat.endurance.score!)" : nil), weight: exerciseScores.squat.endurance.weight, volume: exerciseScores.squat.endurance.volume))
		squatScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Strength", dateDisplay: (exerciseScores.squat.strength.date != nil ? dateFormatter.string(from: exerciseScores.squat.strength.date!) : nil), scoreDisplay: (exerciseScores.squat.strength.score != nil ? "\(exerciseScores.squat.strength.score!)" : nil), weight: exerciseScores.squat.strength.weight, volume: exerciseScores.squat.strength.volume))
		squatScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Power", dateDisplay: (exerciseScores.squat.power.date != nil ? dateFormatter.string(from: exerciseScores.squat.power.date!) : nil), scoreDisplay: (exerciseScores.squat.power.score != nil ? "\(exerciseScores.squat.power.score!)" : nil), weight: exerciseScores.squat.power.weight, volume: exerciseScores.squat.power.volume))
		viewModel.append((squat, squatScores))
		
		let militaryPress = ExerciseInfo(image: Asset.ReportCard.scoreHeaderMilitaryPress.image, title: "Military Press", isWeightLifting: true)
		var militaryPressScores = [ExerciseScoreAthleteCellViewModel]()
		militaryPressScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Stamina", dateDisplay: (exerciseScores.militaryPress.stamina.date != nil ? dateFormatter.string(from: exerciseScores.militaryPress.stamina.date!) : nil), scoreDisplay: (exerciseScores.militaryPress.stamina.score != nil ? "\(exerciseScores.militaryPress.stamina.score!)" : nil), weight: exerciseScores.militaryPress.stamina.weight, volume: exerciseScores.militaryPress.stamina.volume))
		militaryPressScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Endurance", dateDisplay: (exerciseScores.militaryPress.endurance.date != nil ? dateFormatter.string(from: exerciseScores.militaryPress.endurance.date!) : nil), scoreDisplay: (exerciseScores.militaryPress.endurance.score != nil ? "\(exerciseScores.militaryPress.endurance.score!)" : nil), weight: exerciseScores.militaryPress.endurance.weight, volume: exerciseScores.militaryPress.endurance.volume))
		militaryPressScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Strength", dateDisplay: (exerciseScores.militaryPress.strength.date != nil ? dateFormatter.string(from: exerciseScores.militaryPress.strength.date!) : nil), scoreDisplay: (exerciseScores.militaryPress.strength.score != nil ? "\(exerciseScores.militaryPress.strength.score!)" : nil), weight: exerciseScores.militaryPress.strength.weight, volume: exerciseScores.militaryPress.strength.volume))
		militaryPressScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Power", dateDisplay: (exerciseScores.militaryPress.power.date != nil ? dateFormatter.string(from: exerciseScores.militaryPress.power.date!) : nil), scoreDisplay: (exerciseScores.militaryPress.power.score != nil ? "\(exerciseScores.militaryPress.power.score!)" : nil), weight: exerciseScores.militaryPress.power.weight, volume: exerciseScores.militaryPress.power.volume))
		viewModel.append((militaryPress, militaryPressScores))
		
		let mileRun = ExerciseInfo(image: Asset.ReportCard.scoreHeaderMileRun.image, title: "Mile Run", isWeightLifting: false)
		var mileRunScores = [ExerciseScoreAthleteCellViewModel]()
		mileRunScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Track Running", dateDisplay: (exerciseScores.mileRun.trackRunning.date != nil ? dateFormatter.string(from: exerciseScores.mileRun.trackRunning.date!) : nil), scoreDisplay: (exerciseScores.mileRun.trackRunning.score != nil ? FormatMillisecondsForDisplay.convertScoreForDisplayMileRun(score: "\(exerciseScores.mileRun.trackRunning.score!)") : nil), weight: exerciseScores.mileRun.trackRunning.weight, volume: exerciseScores.mileRun.trackRunning.volume))
		mileRunScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Outdoor", dateDisplay: (exerciseScores.mileRun.outdoor.date != nil ? dateFormatter.string(from: exerciseScores.mileRun.outdoor.date!) : nil), scoreDisplay: (exerciseScores.mileRun.outdoor.score != nil ? FormatMillisecondsForDisplay.convertScoreForDisplayMileRun(score: "\(exerciseScores.mileRun.outdoor.score!)") : nil), weight: exerciseScores.mileRun.outdoor.weight, volume: exerciseScores.mileRun.outdoor.volume))
		mileRunScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Treadmill", dateDisplay: (exerciseScores.mileRun.treadmill.date != nil ? dateFormatter.string(from: exerciseScores.mileRun.treadmill.date!) : nil), scoreDisplay: (exerciseScores.mileRun.treadmill.score != nil ? FormatMillisecondsForDisplay.convertScoreForDisplayMileRun(score: "\(exerciseScores.mileRun.treadmill.score!)") : nil), weight: exerciseScores.mileRun.treadmill.weight, volume: exerciseScores.mileRun.treadmill.volume))
		viewModel.append((mileRun, mileRunScores))
		
		let fourtyYardDash = ExerciseInfo(image: Asset.ReportCard.scoreHeaderFortyYardDash.image, title: "40 Yard Dash", isWeightLifting: false)
		var fourtyYardDashScores = [ExerciseScoreAthleteCellViewModel]()
		fourtyYardDashScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Self Timed", dateDisplay: (exerciseScores.fortyYardDash.selfTimed.date != nil ? dateFormatter.string(from: exerciseScores.fortyYardDash.selfTimed.date!) : nil), scoreDisplay: (exerciseScores.fortyYardDash.selfTimed.score != nil ? FormatMillisecondsForDisplay.convertScoreForDisplayFortyYardDash(score: "\(exerciseScores.fortyYardDash.selfTimed.score!)") : nil), weight: exerciseScores.fortyYardDash.selfTimed.weight, volume: exerciseScores.fortyYardDash.selfTimed.volume))
		fourtyYardDashScores.append(ExerciseScoreAthleteCellViewModel(exerciseSubCategoryName: "Cued Time", dateDisplay: (exerciseScores.fortyYardDash.cuedTime.date != nil ? dateFormatter.string(from: exerciseScores.fortyYardDash.cuedTime.date!) : nil), scoreDisplay: (exerciseScores.fortyYardDash.cuedTime.score != nil ? FormatMillisecondsForDisplay.convertScoreForDisplayFortyYardDash(score: "\(exerciseScores.fortyYardDash.cuedTime.score!)") : nil), weight: exerciseScores.fortyYardDash.cuedTime.weight, volume: exerciseScores.fortyYardDash.cuedTime.volume))
		viewModel.append((fourtyYardDash, fourtyYardDashScores))
		
		return viewModel
	}
}
