//
//  ExercisesCoordinatorTests.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-10.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import XCTest
@testable import REPerformance

class ExercisesCoordinatorTests: XCTestCase {
    
    var exercisesCoordinator:ExercisesCoordinator = ExercisesCoordinator(dataProvider: ExercisesDataProvider())
    
    
    
    //MARK: viewData
    func testViewDataCardio(){
        //given 
        let exerciseCategory:ExerciseCategory = .MileRun
        let testFormat:ExerciseTestFormat = .TrackRunning
        let exerciseResult:ExerciseResult = ExerciseResult(totalRank: 32, rank: 111)
        let exerciseScore:ExerciseScore = ExerciseScore(minutes: 3, seconds: 34, milliseconds: 243, heartrate: nil, reps: nil)
        
        //when
        let viewData:SubmissionResultsViewData = SubmissionResultsViewData(exerciseCategory: exerciseCategory, exerciseTestFormat: testFormat, exerciseResult: exerciseResult, exerciseScore: exerciseScore)
        
        //Then
        XCTAssertEqual(viewData.titleText, L10n.testInformationMileRunTitle.string, "Incorrect title")
        XCTAssertEqual(viewData.dateText, DateFormatter.exercisesResultsDateFormatter().string(from: Date()))
        let scoreString:String = "\(String(format: "%01d", exerciseScore.minutes!)):\(String(format: "%02d", exerciseScore.seconds!)):\(String(format: "%03d", exerciseScore.milliseconds!))"
        XCTAssertEqual(viewData.scoreText, scoreString)
        XCTAssertFalse(viewData.hideTimeLabel)
        XCTAssertEqual(viewData.yourCurrentRankText, String(exerciseResult.rank))
        XCTAssertEqual(viewData.totalRanksText, "out of \(exerciseResult.totalRank)")
        XCTAssertEqual(viewData.exerciseCategoryText, "Track Running")
        
    }
    
    func testViewDataReps(){
        //given
        let exerciseCategory:ExerciseCategory = .BenchPress
        let testFormat:ExerciseTestFormat = .Strength
        let exerciseResult:ExerciseResult = ExerciseResult(totalRank: 10, rank: 202)
        let exerciseScore:ExerciseScore = ExerciseScore(minutes: nil, seconds: nil, milliseconds: nil, heartrate: nil, reps: 27)
        
        //when
        let viewData:SubmissionResultsViewData = SubmissionResultsViewData(exerciseCategory: exerciseCategory, exerciseTestFormat: testFormat, exerciseResult: exerciseResult, exerciseScore: exerciseScore)
        
        //Then
        XCTAssertEqual(viewData.titleText, L10n.testInformationBenchPressTitle.string, "Incorrect title")
        XCTAssertEqual(viewData.dateText, DateFormatter.exercisesResultsDateFormatter().string(from: Date()))
        let scoreString:String = "\(exerciseScore.reps!)"
        XCTAssertEqual(viewData.scoreText, scoreString)
        XCTAssertTrue(viewData.hideTimeLabel)
        XCTAssertEqual(viewData.yourCurrentRankText, String(exerciseResult.rank))
        XCTAssertEqual(viewData.totalRanksText, "out of \(exerciseResult.totalRank)")
        XCTAssertEqual(viewData.exerciseCategoryText, "Strength")
    }
    
    func testViewDataCardioWhenGivenScoreAsReps(){
        //given
        let exerciseCategory:ExerciseCategory = .MileRun
        let testFormat:ExerciseTestFormat = .TrackRunning
        let exerciseResult:ExerciseResult = ExerciseResult(totalRank: 32, rank: 111)
        let exerciseScore:ExerciseScore = ExerciseScore(minutes: nil, seconds: nil, milliseconds: nil, heartrate: nil, reps: 27)
        
        //when
        let viewData:SubmissionResultsViewData = SubmissionResultsViewData(exerciseCategory: exerciseCategory, exerciseTestFormat: testFormat, exerciseResult: exerciseResult, exerciseScore: exerciseScore)
        
        //Then
        XCTAssertEqual(viewData.titleText, L10n.testInformationMileRunTitle.string, "Incorrect title")
        XCTAssertEqual(viewData.dateText, DateFormatter.exercisesResultsDateFormatter().string(from: Date()))
        let scoreString:String = "\(String(format: "%01d", 0)):\(String(format: "%02d", 0)):\(String(format: "%03d", 0))"
        XCTAssertEqual(viewData.scoreText, scoreString)
        XCTAssertFalse(viewData.hideTimeLabel)
        XCTAssertEqual(viewData.yourCurrentRankText, String(exerciseResult.rank))
        XCTAssertEqual(viewData.totalRanksText, "out of \(exerciseResult.totalRank)")
        XCTAssertEqual(viewData.exerciseCategoryText, "Track Running")
    }
    
    func testViewDataRepsWhenGivenScoreAsCardio(){
        //given
        let exerciseCategory:ExerciseCategory = .BenchPress
        let testFormat:ExerciseTestFormat = .Strength
        let exerciseResult:ExerciseResult = ExerciseResult(totalRank: 10, rank: 202)
        let exerciseScore:ExerciseScore = ExerciseScore(minutes: 3, seconds: 34, milliseconds: 243, heartrate: nil, reps: nil)
        
        //when
        let viewData:SubmissionResultsViewData = SubmissionResultsViewData(exerciseCategory: exerciseCategory, exerciseTestFormat: testFormat, exerciseResult: exerciseResult, exerciseScore: exerciseScore)
        
        //Then
        XCTAssertEqual(viewData.titleText, L10n.testInformationBenchPressTitle.string, "Incorrect title")
        XCTAssertEqual(viewData.dateText, DateFormatter.exercisesResultsDateFormatter().string(from: Date()))
        let scoreString:String = ""
        XCTAssertEqual(viewData.scoreText, scoreString)
        XCTAssertTrue(viewData.hideTimeLabel)
        XCTAssertEqual(viewData.yourCurrentRankText, String(exerciseResult.rank))
        XCTAssertEqual(viewData.totalRanksText, "out of \(exerciseResult.totalRank)")
        XCTAssertEqual(viewData.exerciseCategoryText, "Strength")
    }
    
    
    
}
