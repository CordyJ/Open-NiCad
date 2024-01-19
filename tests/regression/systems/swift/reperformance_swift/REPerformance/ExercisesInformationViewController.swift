//
//  ExercisesInformationViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-02.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

struct ExerciseInformation {
    let title: String
    let description: String
    let funFacts:String
    let backgroundImage: UIImage
    let activityLineImage: UIImage
}

class ExercisesInformationViewController: UIViewController {
    
    @IBOutlet private var backgroundImageView: UIImageView?
    @IBOutlet private var titleLabel: UILabel?
    @IBOutlet private var descriptionLabel: UILabel?
    @IBOutlet private var activityLineImageView: UIImageView?
    
    @IBOutlet private var funFactsTitleLabel:UILabel?
    @IBOutlet private var funFactsDescriptionLabel:UILabel?
    
    @IBOutlet private var getStartedButton: UIButton?
    
    var exerciseInformation: ExerciseInformation?
    var exerciseCategory: ExerciseCategory?
    var getStarted: (()->())?
    
    override var prefersStatusBarHidden : Bool {
        return true
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)

        loadExerciseInformation(exerciseInformation: exerciseInformation)
        self.titleLabel?.textColor = UIColor.white
        self.descriptionLabel?.textColor = UIColor.white
        self.funFactsTitleLabel?.textColor = UIColor.white
        self.funFactsDescriptionLabel?.textColor = UIColor.white
    }
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        guard let exerciseCategory = exerciseCategory else {
            return
        }
        switch exerciseCategory {
        case .MileRun:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsMileRun.Description, className: String(describing: self))
        case .FortyYardDash:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsFortyYardDash.Description, className: String(describing: self))
        case .BenchPress:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsBenchPress.Description, className: String(describing: self))
        case .DeadLift:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsDeadlift.Description, className: String(describing: self))
        case .Squat:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsSquat.Description, className: String(describing: self))
        case .MilitaryPress:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsMilitaryPress.Description, className: String(describing: self))
        }
    }
    
    fileprivate func loadExerciseInformation(exerciseInformation: ExerciseInformation?){
        if let exerciseInformation = exerciseInformation {
            self.titleLabel?.text = exerciseInformation.title
            self.descriptionLabel?.text = exerciseInformation.description
            self.backgroundImageView?.image = exerciseInformation.backgroundImage
            self.activityLineImageView?.image = exerciseInformation.activityLineImage
            self.funFactsDescriptionLabel?.text = exerciseInformation.funFacts
        }
    }

    
    
    @IBAction func getStartedTapped(_ sender: UIButton){

        getStarted?()
    }
}
