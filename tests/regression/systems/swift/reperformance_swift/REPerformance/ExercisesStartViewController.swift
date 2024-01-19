//
//  ExercisesStartViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-03.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

struct ExercisesStartViewControllerContent {
    let title:String
    let instructionsLabel1Text: String
    let instructionsLabel2Text: String?
    let button1Text: String?
    let button2Text: String?
    let button3Text: String?
    let button4Text: String?
    let exerciseTestFormatButton1: ExerciseTestFormat
    let exerciseTestFormatButton2: ExerciseTestFormat
    let exerciseTestFormatButton3: ExerciseTestFormat?
    let exerciseTestFormatButton4: ExerciseTestFormat?
}

enum VideoState {
    case unDetermined
    case upload
    case notUpload
}

class ExercisesStartViewController: UIViewController {
	
	override var preferredStatusBarStyle: UIStatusBarStyle {
		return .lightContent
	}
    
    @IBOutlet private var instructionsLabelOne: UILabel!
    @IBOutlet private var instructionsLabelTwo: UILabel!
    @IBOutlet private var button1: UIButton!
    @IBOutlet private var button2: UIButton!
    @IBOutlet private var button3: UIButton!
    @IBOutlet private var button4: UIButton!
    @IBOutlet private var videoLabel: UILabel!
    @IBOutlet private var uploadButton: UIButton!
    @IBOutlet private var notUploadButton: UIButton!
    @IBOutlet private var nextButton: UIButton!
    
    var buttons: Array<UIButton> = []
    var videoButtons: Array<UIButton> = []
    
    var uploadState: VideoState = .unDetermined
    
    var exercisesStartViewControllerContent: ExercisesStartViewControllerContent? {
        didSet {
            populateFields()
        }
    }
    var exerciseCategory: ExerciseCategory?
    var exerciseTestFormat: ExerciseTestFormat?
    
    var nextButtonClosure: ((ExerciseTestFormat, VideoState)->())?
    var retrieveExerciseContent: ((ExerciseCategory)->())?
    
    override func viewDidLoad() {
        super.viewDidLoad()

        buttons = [button1, button2, button3, button4]
        videoButtons = [uploadButton, notUploadButton]

        setUpView()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        guard let exercise = exerciseCategory else {
            return
        }
        retrieveExerciseContent?(exercise)
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        guard let exerciseCategory = exerciseCategory else {
            return
        }
        switch exerciseCategory {
        case .MileRun:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsMileRun.Setup, className: String(describing: self))
        case .FortyYardDash:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsFortyYardDash.Setup, className: String(describing: self))
        case .BenchPress:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsBenchPress.Setup, className: String(describing: self))
        case .DeadLift:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsDeadlift.Setup, className: String(describing: self))
        case .Squat:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsSquat.Setup, className: String(describing: self))
        case .MilitaryPress:
            REPAnalytics.trackScreenWithName(screenName: ScreenName.TestsMilitaryPress.Setup, className: String(describing: self))
        }
    }
    
    private func setUpView() {
        self.instructionsLabelOne.textColor = .white
        self.instructionsLabelTwo.textColor = .white
        self.videoLabel.textColor = .white
        
        self.nextButton.setUpOrangeREPerformanceButton()
        self.nextButton.setEnabled(enabled: false)
        
        uploadButton.imageView?.contentMode = .scaleAspectFit
        notUploadButton.imageView?.contentMode = .scaleAspectFit
        
        applyLayout(buttons:buttons)
        applyLayout(buttons:videoButtons)
    }
    
    private func applyLayout(buttons: Array<UIButton>) {
        for currentButton in buttons{
            currentButton.roundCornersAndApplyBorder()
            currentButton.textColor = UIColor.white
            currentButton.titleLabel?.lineBreakMode = NSLineBreakMode.byWordWrapping
            currentButton.titleLabel?.numberOfLines = 2
            currentButton.titleLabel?.textAlignment = NSTextAlignment.center
        }
    }
    
    private func populateFields() {
        guard let exercisesStartViewControllerContent = self.exercisesStartViewControllerContent else {
            UIAlertController.showAlert(L10n.exerciseInfoErrorTitle, message: L10n.exerciseInfoErrorMessage, inViewController: self)
            return
        }
        self.title = exercisesStartViewControllerContent.title
        self.instructionsLabelOne?.text = exercisesStartViewControllerContent.instructionsLabel1Text
        
        if let instructionsLabel2Text = self.exercisesStartViewControllerContent?.instructionsLabel2Text {
            self.instructionsLabelTwo?.text = instructionsLabel2Text
        } else {
            self.instructionsLabelTwo?.removeFromSuperview()
        }
        
        self.button1?.setTitle(exercisesStartViewControllerContent.button1Text, for: .normal)
        self.button2?.setTitle(exercisesStartViewControllerContent.button2Text, for: .normal)
        
        if let button3Text = self.exercisesStartViewControllerContent?.button3Text {
            self.button3?.setTitle(button3Text, for: .normal)
        } else {
            button3.superview?.removeFromSuperview()
        }
        
        if let button4Text = self.exercisesStartViewControllerContent?.button4Text {
            self.button4?.setTitle(button4Text, for: .normal)
        } else {
            button4.superview?.removeFromSuperview()
        }
    }
    
    private func setToggleButtonSelected(button: UIButton?, buttons: Array<UIButton>) {
        for currentButton in buttons{
            if currentButton == button{
                currentButton.backgroundColor = UIColor.init(named: .rePerformanceOrange)
            }
            else
            {
                currentButton.backgroundColor = UIColor.clear
            }
        }
        checkNextButtonState()
    }
    
    private func checkNextButtonState() {
        let shouldEnable = self.exerciseTestFormat != nil && uploadState != .unDetermined
        self.nextButton.setEnabled(enabled: shouldEnable)
    }
    
    @IBAction func button1Tapped(_ sender: UIButton) {
        exerciseTestFormat = exercisesStartViewControllerContent?.exerciseTestFormatButton1
        setToggleButtonSelected(button: button1, buttons: buttons)
    }
    
    @IBAction func button2Tapped(_ sender: UIButton) {
        exerciseTestFormat = exercisesStartViewControllerContent?.exerciseTestFormatButton2
        setToggleButtonSelected(button: button2, buttons: buttons)

    }
    
    @IBAction func button3Tapped(_ sender: UIButton) {
        exerciseTestFormat = exercisesStartViewControllerContent?.exerciseTestFormatButton3
        setToggleButtonSelected(button: button3, buttons: buttons)

    }
    
    @IBAction func button4Tapped(_ sender: UIButton) {
        exerciseTestFormat = exercisesStartViewControllerContent?.exerciseTestFormatButton4
        setToggleButtonSelected(button: button4, buttons: buttons)
    }
    
    @IBAction func uploadTapped(_ sender: UIButton) {
        uploadState = .upload
        setToggleButtonSelected(button: uploadButton, buttons: videoButtons)
    }

    @IBAction func notUploadTapped(_ sender: UIButton) {
        uploadState = .notUpload
        setToggleButtonSelected(button: notUploadButton, buttons: videoButtons)
    }
    
    @IBAction func nextTapped(_ sender: UIButton) {
        guard let exerciseTestFormat = self.exerciseTestFormat, uploadState != .unDetermined else {
            return
        }
        
        nextButtonClosure?(exerciseTestFormat, uploadState)
    }

}
