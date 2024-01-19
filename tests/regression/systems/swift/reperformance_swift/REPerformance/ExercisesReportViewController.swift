//
//  ExercisesReportViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-03.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

struct ExerciseScore {
    var minutes: Int?
    var seconds: Int?
    var milliseconds: Int?
    var heartrate: Int?
    var reps:Int?
}

class ExercisesReportViewController: UIViewController {
	
	override var preferredStatusBarStyle: UIStatusBarStyle {
		return .lightContent
	}
    
    @IBOutlet internal var instructionsLabel: UILabel?
    @IBOutlet internal var submitScoreButton: UIButton?
    
    var exerciseScore:ExerciseScore = ExerciseScore(minutes: nil, seconds: nil, milliseconds: nil, heartrate: nil, reps:nil)
    var exerciseCategory:ExerciseCategory?

    var submit: ((ExerciseScore)->())?

    override func viewDidLoad() {
        super.viewDidLoad()
        setUpView()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        wipeView()
    }
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        guard let exerciseCategory = exerciseCategory else {
            return
        }
        switch exerciseCategory {
        case .MileRun:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsMileRun.Input, className: String(describing: self))
        case .FortyYardDash:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsFortyYardDash.Input, className: String(describing: self))
        case .BenchPress:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsBenchPress.Input, className: String(describing: self))
        case .DeadLift:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsDeadlift.Input, className: String(describing: self))
        case .Squat:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsSquat.Input, className: String(describing: self))
        case .MilitaryPress:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsMilitaryPress.Input, className: String(describing: self))
        }
    }
    
    func setUpView()
    {
        instructionsLabel?.textColor = UIColor.white
        
        submitScoreButton?.setUpOrangeREPerformanceButton()
        submitScoreButton?.setEnabled(enabled: false)
    }
    
    func wipeView()
    {
        if let exerciseCategory = self.exerciseCategory {
            switch exerciseCategory {
            case .MileRun:
                self.title = L10n.testInformationMileRunTitle
            case .FortyYardDash:
                self.title = L10n.testInformationYardDashTitle
            case .BenchPress:
                self.title = L10n.testInformationBenchPressTitle
            case .DeadLift:
                self.title = L10n.testInformationDeadliftTitle
            case .Squat:
                self.title = L10n.testInformationSquatTitle
            case .MilitaryPress:
                self.title = L10n.testInformationMilitaryPressTitle
            }
        }
        
        submitScoreButton?.setEnabled(enabled: false)
        exerciseScore = ExerciseScore(minutes: nil, seconds: nil, milliseconds: nil, heartrate: nil, reps: nil)
    }
    
    
    @IBAction func submitScoreTapped(_ sender: UIButton)
    {
        submitScoreButton?.setEnabled(enabled: false)
        if exerciseScore.milliseconds != nil{
                submit?(exerciseScore)
        } else {
            if exerciseScore.reps == nil {
                exerciseScore.milliseconds = 0
            }
            submit?(exerciseScore)
        }
    }
}

