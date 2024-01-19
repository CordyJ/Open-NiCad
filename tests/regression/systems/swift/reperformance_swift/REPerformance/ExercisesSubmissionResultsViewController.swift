//
//  ExercisesSubmissionResultsViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-05.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

struct SubmissionResultsViewData {
    let titleText:String
    let dateText:String
    let scoreText:String
    let hideTimeLabel:Bool
    let yourCurrentRankText:String
    let totalRanksText:String
    let exerciseCategoryText:String
    let creditsEarnedText:String
    let personalRecord:Bool
    let videoExists:Bool
    
    init(exerciseCategory:ExerciseCategory, exerciseTestFormat:ExerciseTestFormat, exerciseResult:ExerciseResult, exerciseScore:ExerciseScore, videoExists:Bool) {
        switch exerciseCategory{
        case .MileRun:
            titleText = L10n.testInformationMileRunTitle
        case .FortyYardDash:
            titleText = L10n.testInformationYardDashTitle
        case .BenchPress:
            titleText = L10n.testInformationBenchPressTitle
        case .DeadLift:
            titleText = L10n.testInformationDeadliftTitle
        case .Squat:
            titleText = L10n.testInformationSquatTitle
        case .MilitaryPress:
            titleText = L10n.testInformationMilitaryPressTitle
        }
        
        dateText = DateFormatter.exercisesResultsDateFormatter().string(from: Date())
        
        switch exerciseCategory {
        case .MileRun:
            let minutes:Int
            let seconds:Int
            let milliseconds:Int
            
            if exerciseScore.minutes == nil {
                minutes = 0
            } else {
                minutes = (exerciseScore.minutes)!
            }
            if exerciseScore.seconds == nil {
                seconds = 0
            } else {
                seconds = (exerciseScore.seconds)!
            }
            if exerciseScore.milliseconds == nil {
                milliseconds = 0
            } else {
                milliseconds = (exerciseScore.milliseconds)!
            }
            
            let formattedMinutes = String(format: "%01d", minutes)
            let formattedSeconds = String(format: "%02d", seconds)
            let formattedMilliseconds = String(format: "%02d", milliseconds)
            scoreText = "\(formattedMinutes):\(formattedSeconds).\(formattedMilliseconds)"
            hideTimeLabel = false
        case .FortyYardDash:
            let seconds:Int
            let milliseconds:Int
            
            if exerciseScore.seconds == nil {
                seconds = 0
            } else {
                seconds = (exerciseScore.seconds)!
            }
            if exerciseScore.milliseconds == nil {
                milliseconds = 0
            } else {
                milliseconds = (exerciseScore.milliseconds)!
            }
            
            let formattedSeconds = String(format: "%02d", seconds)
            let formattedMilliseconds = String(format: "%02d", milliseconds)
            scoreText = "\(formattedSeconds).\(formattedMilliseconds)"
            hideTimeLabel = false
        case .BenchPress, .DeadLift, .Squat, .MilitaryPress:
            if let reps = exerciseScore.reps {
                scoreText = "\(reps)"
            } else {
                scoreText = ""
            }
            hideTimeLabel = true
        }
        
        yourCurrentRankText = "\(exerciseResult.rank)"
        totalRanksText = "out of \(exerciseResult.totalRank)"
        
        
        switch exerciseTestFormat {
        case .TrackRunning:
            exerciseCategoryText = "Track Running"
        case .Outdoor:
            exerciseCategoryText = "Outdoor Running"
        case .Treadmill:
            exerciseCategoryText = "Treadmill Running"
        case .SelfTimed:
            exerciseCategoryText = "Self Timed"
        case .CuedTime:
            exerciseCategoryText = "Cued Time"
        case .Stamina:
            exerciseCategoryText = "Stamina"
        case .Endurance:
            exerciseCategoryText = "Endurance"
        case .Strength:
            exerciseCategoryText = "Strength"
        case .Power:
            exerciseCategoryText = "Power"
        }
        
        creditsEarnedText = "\(exerciseResult.creditsEarned) credits earned"
        personalRecord = exerciseResult.personalRecord
        
        self.videoExists = videoExists
    }
}

class ExercisesSubmissionResultsViewController: UIViewController {
    
    @IBOutlet private var titleLabel: UILabel?
    @IBOutlet private var exerciseCategoryTitleLabel: UILabel?
    @IBOutlet private var dateLabel: UILabel?
    @IBOutlet private var yourScoreTitleLabel: UILabel?
    @IBOutlet private var timeLabel: UILabel?
    @IBOutlet private var scoreLabel: UILabel?
    @IBOutlet private var personalRecordLabel: UILabel?
    @IBOutlet private var currentRankingTitleLabel: UILabel?
    @IBOutlet private var yourCurrentRankLabel: UILabel?
    @IBOutlet private var totalRanksLabel: UILabel?
    @IBOutlet private var creditsEarnedLabel: UILabel?
    @IBOutlet private var shareVideoInstagramButton:UIButton?
    @IBOutlet private var shareVideoSocialMediaButton:UIButton?
    @IBOutlet private var doneButton:UIButton?
    @IBOutlet private var scrollView:UIScrollView?
    @IBOutlet private var creditsEarnedImageView:UIImageView?
    @IBOutlet private var sharingView:UIView?
    @IBOutlet private var shareVideoLabel:UILabel?
    
    var viewData: SubmissionResultsViewData?
    var exerciseCategory: ExerciseCategory?
	
	var compareToOthers:(()->())?
    var shareVideoInstagram: (()->())?
    var shareVideoSocialMedia: (()->())?
    var done: (()->())?
	
	
    override var preferredStatusBarStyle: UIStatusBarStyle {
        return .lightContent
    }

    override func viewDidLoad() {
        super.viewDidLoad()
		
        setUpView()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
		
        setLabels()
    }
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
		
        guard let exerciseCategory = exerciseCategory else {
            return
        }
        switch exerciseCategory {
        case .MileRun:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsMileRun.Score, className: String(describing: self))
        case .FortyYardDash:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsFortyYardDash.Score, className: String(describing: self))
        case .BenchPress:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsBenchPress.Score, className: String(describing: self))
        case .DeadLift:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsDeadlift.Score, className: String(describing: self))
        case .Squat:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsSquat.Score, className: String(describing: self))
        case .MilitaryPress:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsMilitaryPress.Score, className: String(describing: self))
        }
    }

    func setUpView() {
        titleLabel?.textColor = UIColor.white
        exerciseCategoryTitleLabel?.textColor = UIColor.white
        dateLabel?.textColor = UIColor.init(named: .rePerformanceOrange)
        yourScoreTitleLabel?.textColor = UIColor.white
        timeLabel?.textColor = UIColor.white
        scoreLabel?.textColor = UIColor.init(named: .rePerformanceOrange)
        personalRecordLabel?.textColor = UIColor.init(named: .rePerformanceOrange)
        currentRankingTitleLabel?.textColor = UIColor.white
        yourCurrentRankLabel?.textColor = UIColor.white
        totalRanksLabel?.textColor = UIColor.white
        creditsEarnedLabel?.textColor = UIColor.init(named: .rePerformanceOrange)
        doneButton?.textColor = UIColor.white
        shareVideoSocialMediaButton?.imageView?.contentMode = .scaleAspectFit
        shareVideoInstagramButton?.imageView?.contentMode = .scaleAspectFit
    }
    
    func setLabels() {
        let scrollViewTop = CGPoint.zero
        scrollView?.setContentOffset(scrollViewTop, animated: false)
        
        guard let viewData = self.viewData else {
            return
        }
		
        titleLabel?.text = viewData.titleText
        dateLabel?.text = viewData.dateText
        scoreLabel?.text = viewData.scoreText
        
        timeLabel?.isHidden = viewData.hideTimeLabel
        personalRecordLabel?.isHidden = !viewData.personalRecord

        yourCurrentRankLabel?.text = viewData.yourCurrentRankText
        totalRanksLabel?.text = viewData.totalRanksText
        exerciseCategoryTitleLabel?.text = viewData.exerciseCategoryText
        creditsEarnedLabel?.text = viewData.creditsEarnedText
		
		if !viewData.videoExists {
			sharingView?.isHidden = true
			shareVideoLabel?.isHidden = true
		}
    }
	
	
	@IBAction private func compareToOthersTapped(_ sender:UIButton?){
		self.compareToOthers?()
	}
    
    @IBAction func shareVideoInstagramButtonTapped(_ sender:UIButton){
        shareVideoInstagram?()
    }
    
    @IBAction func shareVideoSocialMediaButtonTapped(_ sender:UIButton){
        shareVideoSocialMedia?()
    }
    
    @IBAction func doneButtonTapped(_ sender: UIButton) {
        done?()
    }
}
