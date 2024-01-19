//
//  ExercisesViewController.swift
//
//  Created by Alan Yeung on 2017-05-01.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit


class ExercisesViewController: UIViewController {
    
    @IBOutlet private var repLogoImageView: UIImageView?
    
    @IBOutlet private var mileRunButton: UIButton?
    @IBOutlet private var yardDashButton: UIButton?
    @IBOutlet private var benchPressButton: UIButton?
    @IBOutlet private var deadliftButton: UIButton?
    @IBOutlet private var squatButton: UIButton?
    @IBOutlet private var militaryPressButton: UIButton?
    @IBOutlet private var challengesButton: UIButton?
    
    @IBOutlet weak var creditLabel: UILabel!
    @IBOutlet weak var dollarLabel: UILabel!
    
    var viewExerciseInformation: ((ExerciseCategory)->())?
    var showChallenges: (()->())?
    var clearVideoData: (()->())?

    override var prefersStatusBarHidden : Bool {
        return true
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        repLogoImageView?.image = #imageLiteral(resourceName: "repLogo")
        challengesButton?.setTitle(L10n.challengeButtonTitle, for: .normal)
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        self.navigationController?.setNavigationBarHidden(true, animated: false)
        // When picking a new exercise, avoids carrying over data from the previously incomplete score submission.
        self.clearVideoData?()
        
        CreditsUpdater.updateCredits { (success) in
            if let userCredits = UserDefaults.standard.userCredits {
                self.creditLabel?.text  = String(format: "%@: %@", L10n.totalCredits, userCredits)
            } else {
                self.creditLabel?.text  = ""
            }
            if let dollars = UserDefaults.standard.userDollars {
                self.dollarLabel?.text = String(format: "%@: $%.2f", L10n.dollarValue, dollars)
            } else {
                self.dollarLabel?.text = ""
            }
        }
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        REPAnalytics.trackScreenWithName(screenName: ScreenName.HomePage.Test, className: String(describing: self))
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        self.navigationController?.setNavigationBarHidden(false, animated: false)
    }

    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        mileRunButton?.addDashedBorder(strokeColor: .white, lineWidth: 1.0)
        yardDashButton?.addDashedBorder(strokeColor: .white, lineWidth: 1.0)
        benchPressButton?.addDashedBorder(strokeColor: .white, lineWidth: 1.0)
        deadliftButton?.addDashedBorder(strokeColor: .white, lineWidth: 1.0)
        squatButton?.addDashedBorder(strokeColor: .white, lineWidth: 1.0)
        militaryPressButton?.addDashedBorder(strokeColor: .white, lineWidth: 1.0)
    }
    
    //MARK: Actions
    
    @IBAction func mileRunTapped(_ sender: UIButton){
        viewExerciseInformation?(.MileRun)
    }
    
    @IBAction func yardDashTapped(_ sender: UIButton){
        viewExerciseInformation?(.FortyYardDash)
    }
    
    @IBAction func benchPressTapped(_ sender: UIButton){
        viewExerciseInformation?(.BenchPress)
    }
    
    @IBAction func deadLiftTapped(_ sender: UIButton){
        viewExerciseInformation?(.DeadLift)
    }
    
    @IBAction func squatTapped(_ sender: UIButton){
        viewExerciseInformation?(.Squat)
    }
    
    @IBAction func militaryPressTapped(_ sender: UIButton){
        viewExerciseInformation?(.MilitaryPress)
    }

    @IBAction func challengesTapped(_ sender: UIButton){
        showChallenges?()
    }
}
