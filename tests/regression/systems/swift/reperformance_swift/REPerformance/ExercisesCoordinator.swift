//
//  ExercisesCoordinator.swift
//  REPerformance
//
//  Created by Francis Chary on 2017-05-02.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import NVActivityIndicatorView
import MobileCoreServices
import Photos

class ExercisesCoordinator: NSObject {

    let navigationController: UINavigationController
    let exercisesDataProvider: ExercisesDataProvider
    let exercisesViewController: ExercisesViewController
    let challengesCoordinator: ChallengesCoordinator

    var exerciseCategory: ExerciseCategory?
    var exerciseTestFormat: ExerciseTestFormat?
    var exerciseVimeoID: String?
    var exerciseCacheURL: URL?

    var setReportCardAndCreditsNeedsUpdate: (()->())?
    
    var videoSubmissionWarningViewController:REPerformanceWarningViewController?
    
    var videoURL:URL?
    
    init(dataProvider: ExercisesDataProvider) {
        navigationController = UINavigationController()
        navigationController.title = L10n.exercisesTitle
        
        exercisesDataProvider = dataProvider
        challengesCoordinator = ChallengesCoordinator()
        
        exercisesViewController = StoryboardScene.Exercises.exercisesVC.instantiate()
        exercisesViewController.tabBarItem = UITabBarItem(title: L10n.testTabBarItemTitle, image: #imageLiteral(resourceName: "TabBar_Tests"), tag: 0)
        navigationController.viewControllers = [exercisesViewController]
        super.init()
        
        configureExercisesViewController()
    }
    
    func tabBarViewController() -> UIViewController {
        return self.navigationController
    }
    
    func configureExercisesViewController() {
        exercisesViewController.viewExerciseInformation = { exerciseCategory in
            var exerciseInformation:ExerciseInformation?
            switch exerciseCategory {
            case .MileRun:
                exerciseInformation = ExerciseInformation(title: L10n.testInformationMileRunTitle, description: L10n.testInformationMileRunDescription, funFacts: L10n.testInformationMileRunFunFact, backgroundImage: #imageLiteral(resourceName: "mileRunBackground"), activityLineImage: #imageLiteral(resourceName: "activityLineMileRun"))
            case .FortyYardDash:
                exerciseInformation = ExerciseInformation(title: L10n.testInformationYardDashTitle, description: L10n.testInformationYardDashDescription, funFacts: L10n.testInformationYardDashFunFact, backgroundImage: #imageLiteral(resourceName: "yardDashBackground"), activityLineImage: #imageLiteral(resourceName: "activityLineYardDash"))
            case .BenchPress:
                exerciseInformation = ExerciseInformation(title: L10n.testInformationBenchPressTitle, description: L10n.testInformationBenchPressDescription, funFacts: L10n.testInformationBenchPressFunFact, backgroundImage: #imageLiteral(resourceName: "benchPressBackground"), activityLineImage: #imageLiteral(resourceName: "activityLineBenchPress"))
            case .DeadLift:
                exerciseInformation = ExerciseInformation(title: L10n.testInformationDeadliftTitle, description: L10n.testInformationDeadliftDescription, funFacts: L10n.testInformationDeadliftFunFact, backgroundImage: #imageLiteral(resourceName: "deadliftBackground"), activityLineImage: #imageLiteral(resourceName: "activityLineDeadlift"))
            case .Squat:
                exerciseInformation = ExerciseInformation(title: L10n.testInformationSquatTitle, description: L10n.testInformationSquatDescription, funFacts: L10n.testInformationSquatFunFact, backgroundImage: #imageLiteral(resourceName: "squatBackground"), activityLineImage: #imageLiteral(resourceName: "activityLineSquat"))
            case .MilitaryPress:
                exerciseInformation = ExerciseInformation(title: L10n.testInformationMilitaryPressTitle, description: L10n.testInformationMilitaryPressDescription, funFacts: L10n.testInformationMilitaryPressFunFact, backgroundImage: #imageLiteral(resourceName: "militaryPressBackground"), activityLineImage: #imageLiteral(resourceName: "activityLineMilitaryPress"))
            }
            self.exerciseCategory = exerciseCategory
            self.moveToExerciseInformation(exerciseInformation: exerciseInformation)
        }
        exercisesViewController.showChallenges = {
            let vc = self.challengesCoordinator.rootViewController()
            vc.navigationItem.leftBarButtonItem = UIBarButtonItem(image: Asset.Assets.xIcon.image, style: .plain, target: self, action: #selector(self.closeButtonTapped(_:)))
            let navigationController = UINavigationController(rootViewController: vc)
            self.navigationController.present(navigationController, animated: true, completion: nil)
        }
        exercisesViewController.clearVideoData = { [unowned self] in
            self.videoURL = nil
            self.exerciseVimeoID = nil
            self.exerciseCacheURL = nil
        }
    }
    
    func moveToExerciseInformation(exerciseInformation:ExerciseInformation?) {
        
        let exerciseInformationViewController = StoryboardScene.Exercises.exerciseInformationVC.instantiate()
        exerciseInformationViewController.exerciseInformation = exerciseInformation
        exerciseInformationViewController.exerciseCategory = exerciseCategory
        exerciseInformationViewController.getStarted = {
            self.moveToExercisesStartViewController()
        }
        
        navigationController.pushViewController(exerciseInformationViewController, animated: true)
    }
    
    func exercisesStartViewController(exercise: ExerciseCategory, weightContent:WeightResult? = nil) -> ExercisesStartViewControllerContent? {
        var exercisesStartViewControllerContent:ExercisesStartViewControllerContent
        switch exercise {
        case .MileRun:
            exercisesStartViewControllerContent = ExercisesStartViewControllerContent(
                title: L10n.testInformationMileRunTitle,
                instructionsLabel1Text: L10n.exerciseMileRunTestFormatInstructions,
                instructionsLabel2Text: nil,
                button1Text: L10n.exerciseMileRunButton1Title,
                button2Text: L10n.exerciseMileRunButton2Title,
                button3Text: L10n.exerciseMileRunButton3Title,
                button4Text: nil,
                exerciseTestFormatButton1: .TrackRunning,
                exerciseTestFormatButton2: .Outdoor,
                exerciseTestFormatButton3: .Treadmill,
                exerciseTestFormatButton4: nil)
        case .FortyYardDash:
            exercisesStartViewControllerContent = ExercisesStartViewControllerContent(
                title: L10n.testInformationYardDashTitle,
                instructionsLabel1Text: L10n.exerciseYardDashTestFormatInstructionsOne,
                instructionsLabel2Text: L10n.exerciseYardDashTestFormatInstructionsTwo,
                button1Text: L10n.exerciseYardDashButton1Title,
                button2Text: L10n.exerciseYardDashButton2Title,
                button3Text: nil,
                button4Text: nil,
                exerciseTestFormatButton1: .SelfTimed,
                exerciseTestFormatButton2: .CuedTime,
                exerciseTestFormatButton3: nil,
                exerciseTestFormatButton4: nil)
        case .BenchPress:
            guard let content = weightContent else { return nil }
            exercisesStartViewControllerContent = ExercisesStartViewControllerContent(
                title: L10n.testInformationBenchPressTitle,
                instructionsLabel1Text: L10n.exerciseWeightLiftingTestFormatInstructions,
                instructionsLabel2Text: nil,
                button1Text: content.staminaWeightToDisplay(),
                button2Text: content.enduranceWeightToDisplay(),
                button3Text: content.strengthWeightToDisplay(),
                button4Text: content.powerWeightToDisplay(),
                exerciseTestFormatButton1: .Stamina,
                exerciseTestFormatButton2: .Endurance,
                exerciseTestFormatButton3: .Strength,
                exerciseTestFormatButton4: .Power)
        case .DeadLift:
            guard let content = weightContent else { return nil }
            exercisesStartViewControllerContent = ExercisesStartViewControllerContent(
                title: L10n.testInformationDeadliftTitle,
                instructionsLabel1Text: L10n.exerciseWeightLiftingTestFormatInstructions,
                instructionsLabel2Text: nil,
                button1Text: content.staminaWeightToDisplay(),
                button2Text: content.enduranceWeightToDisplay(),
                button3Text: content.strengthWeightToDisplay(),
                button4Text: content.powerWeightToDisplay(),
                exerciseTestFormatButton1: .Stamina,
                exerciseTestFormatButton2: .Endurance,
                exerciseTestFormatButton3: .Strength,
                exerciseTestFormatButton4: .Power)
        case .Squat:
            guard let content = weightContent else { return nil }
            exercisesStartViewControllerContent = ExercisesStartViewControllerContent(
                title: L10n.testInformationSquatTitle,
                instructionsLabel1Text: L10n.exerciseWeightLiftingTestFormatInstructions,
                instructionsLabel2Text: nil,
                button1Text: content.staminaWeightToDisplay(),
                button2Text: content.enduranceWeightToDisplay(),
                button3Text: content.strengthWeightToDisplay(),
                button4Text: content.powerWeightToDisplay(),
                exerciseTestFormatButton1: .Stamina,
                exerciseTestFormatButton2: .Endurance,
                exerciseTestFormatButton3: .Strength,
                exerciseTestFormatButton4: .Power)
        case .MilitaryPress:
            guard let content = weightContent else { return nil }
            exercisesStartViewControllerContent = ExercisesStartViewControllerContent(
                title: L10n.testInformationMilitaryPressTitle,
                instructionsLabel1Text: L10n.exerciseWeightLiftingTestFormatInstructions,
                instructionsLabel2Text: nil,
                button1Text: content.staminaWeightToDisplay(),
                button2Text: content.enduranceWeightToDisplay(),
                button3Text: content.strengthWeightToDisplay(),
                button4Text: content.powerWeightToDisplay(),
                exerciseTestFormatButton1: .Stamina,
                exerciseTestFormatButton2: .Endurance,
                exerciseTestFormatButton3: .Strength,
                exerciseTestFormatButton4: .Power)
        }
        return exercisesStartViewControllerContent
    }
    
    func moveToExercisesStartViewController(){
        let exercisesStartViewController = StoryboardScene.Exercises.exercisesStartVC.instantiate()
        exercisesStartViewController.exerciseCategory = exerciseCategory
        exercisesStartViewController.retrieveExerciseContent = { (exercise) in
            switch exercise {
            case .BenchPress, .DeadLift, .Squat, .MilitaryPress:
                // avoids fetching exercise content again after taking a video (modally presented screen)
                guard exercisesStartViewController.presentedViewController == nil else {
                    return
                }
                
                NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
                self.exercisesDataProvider.retrieveWeight(exercise: exercise, completion: { (weightContent, errorMessage) in
                    NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
                    let exercisesStartViewControllerContent = self.exercisesStartViewController(exercise: exercise, weightContent: weightContent)
                    exercisesStartViewController.exercisesStartViewControllerContent = exercisesStartViewControllerContent
                })

            case .MileRun:
                let exercisesStartViewControllerContent = self.exercisesStartViewController(exercise: exercise)
                exercisesStartViewController.exercisesStartViewControllerContent = exercisesStartViewControllerContent
            case .FortyYardDash:
                let exercisesStartViewControllerContent = self.exercisesStartViewController(exercise: exercise)
                exercisesStartViewController.exercisesStartViewControllerContent = exercisesStartViewControllerContent
            }
        }
        
        exercisesStartViewController.nextButtonClosure = { (exerciseTestFormat, videoState) in
            self.exerciseTestFormat = exerciseTestFormat

            if self.exerciseVimeoID != nil || self.exerciseCacheURL != nil {
                self.moveToSubmission()
            } else if videoState == .upload {
                let captureVideoViewController = UIImagePickerController()
                captureVideoViewController.sourceType = .camera
                captureVideoViewController.mediaTypes = [kUTTypeMovie as String]
                captureVideoViewController.delegate = self
                self.navigationController.present(captureVideoViewController, animated: true)
            } else if videoState == .notUpload {
                self.moveToVideoSubmissionWarning()
            }
        }
        navigationController.pushViewController(exercisesStartViewController, animated: true)
    }
    
    func moveToVideoSubmissionWarning(){
        videoSubmissionWarningViewController = StoryboardScene.Main.rePerformanceWarningVC.instantiate()
        guard let videoSubmissionWarningViewController = videoSubmissionWarningViewController else {
            return
        }
        videoSubmissionWarningViewController.configureView(titleText: L10n.videoVerificationInformationTitle, descriptionText: L10n.videoVerificationInformationMessage, okButtonVisible: true, cancelButtonVisible: false)
        videoSubmissionWarningViewController.setOkButtonTitleText(L10n.videoVerificationInformationOkButtonTitle)
        videoSubmissionWarningViewController.navigationItem.hidesBackButton = true
        
        videoSubmissionWarningViewController.ok = {
            self.moveToSubmission()
        }
        
        navigationController.pushViewController(videoSubmissionWarningViewController, animated: true)
    }
    
    func moveToSubmission() {
        guard let exerciseCategory = self.exerciseCategory else{
            return
        }
        
        if let videoSubmissionWarningViewController = videoSubmissionWarningViewController, let index = navigationController.viewControllers.index(of: videoSubmissionWarningViewController){
            navigationController.viewControllers.remove(at: index)
        }
        
        switch exerciseCategory{
        case .MileRun:
            self.moveToExercisesReportMileRun()
        case .FortyYardDash:
            self.moveToExercisesReportFortyYardDash()
        case .BenchPress, .DeadLift, .Squat, .MilitaryPress:
            self.moveToExercisesReportReps()
        }
    }
    
    func moveToExercisesReportMileRun(){
        let exercisesReportMileRunViewController = StoryboardScene.Exercises.exercisesReportMileRunVC.instantiate()
        exercisesReportMileRunViewController.exerciseCategory = exerciseCategory
        exercisesReportMileRunViewController.submit = {exerciseScore in
            self.submitExercisesToServerFromViewController(viewController: exercisesReportMileRunViewController, exerciseScore: exerciseScore)
        }
        navigationController.pushViewController(exercisesReportMileRunViewController, animated: true)
    }
    
    func moveToExercisesReportFortyYardDash(){
        let exercisesReportFortyYardDashViewController = StoryboardScene.Exercises.exercisesFortyYardDashVC.instantiate()
        exercisesReportFortyYardDashViewController.exerciseCategory = exerciseCategory
        exercisesReportFortyYardDashViewController.submit = {exerciseScore in
            self.submitExercisesToServerFromViewController(viewController: exercisesReportFortyYardDashViewController, exerciseScore: exerciseScore)
        }
        navigationController.pushViewController(exercisesReportFortyYardDashViewController, animated: true)
    }
    
    func moveToExercisesReportReps(){
        let exercisesReportRepsViewController = StoryboardScene.Exercises.exercisesReportRepsVC.instantiate()
        exercisesReportRepsViewController.exerciseCategory = exerciseCategory
        exercisesReportRepsViewController.submit = {exerciseScore in
            self.submitExercisesToServerFromViewController(viewController: exercisesReportRepsViewController, exerciseScore: exerciseScore)
            
        }
        navigationController.pushViewController(exercisesReportRepsViewController, animated: true)
    }
    
    func moveToSubmissionResults(submissionResultsViewData:SubmissionResultsViewData){
        let exercisesSubmissionResultsViewController = StoryboardScene.Exercises.exercisesSubmissionResultsVC.instantiate()
        exercisesSubmissionResultsViewController.viewData = submissionResultsViewData
        exercisesSubmissionResultsViewController.exerciseCategory = self.exerciseCategory
        
        exercisesSubmissionResultsViewController.done = {
            CacheSubmissionManager.deleteVideo(videoURL: self.videoURL)
            self.videoURL = nil
            exercisesSubmissionResultsViewController.dismiss(animated: true, completion: {
                self.navigationController.popToViewController(self.exercisesViewController, animated: true)
            })
        }
		
		exercisesSubmissionResultsViewController.compareToOthers = {
			let leaderboardCoordinator = LeaderboardCoordinator()
			leaderboardCoordinator.startGlobal(presentingViewController: exercisesSubmissionResultsViewController)
		}
        
        exercisesSubmissionResultsViewController.shareVideoInstagram = {
            
            switch PHPhotoLibrary.authorizationStatus() {
            case .authorized:
                self.saveVideoToLibrary(fromViewController: exercisesSubmissionResultsViewController)
            case .notDetermined:
                let alertController = UIAlertController(title: nil, message: L10n.requestUsePhotosLibrary, preferredStyle: .alert)
                let okAction = UIAlertAction(title: "Ok", style: .default, handler: { (_) in
                    PHPhotoLibrary.requestAuthorization({ (status) in
                        if status == .authorized {
                            self.saveVideoToLibrary(fromViewController: exercisesSubmissionResultsViewController)
                        } else {
                            UIAlertController.showAlert(nil, message: L10n.requestUsePhotosLibraryDenied, inViewController: exercisesSubmissionResultsViewController)
                        }
                    })
                })
                alertController.addAction(okAction)
                exercisesSubmissionResultsViewController.present(alertController, animated: true, completion: nil)
            case .denied, .restricted:
                UIAlertController.showAlert(nil, message: L10n.requestUsePhotosLibraryDenied, inViewController: exercisesSubmissionResultsViewController)
            }
        }
        
        exercisesSubmissionResultsViewController.shareVideoSocialMedia = {
            if let videoURL = self.videoURL {
                let activityController = UIActivityViewController(activityItems: [videoURL], applicationActivities: nil)
                exercisesSubmissionResultsViewController.present(activityController, animated: true, completion: nil)
            }
        }
        
        navigationController.present(exercisesSubmissionResultsViewController, animated: true, completion: nil)
    }
    
    func saveVideoToLibrary(fromViewController:UIViewController){
        guard let videoURL = self.videoURL else {
            return
        }
        
        PHPhotoLibrary.shared().performChanges({
            PHAssetChangeRequest.creationRequestForAssetFromVideo(atFileURL: videoURL)
        }, completionHandler: { (saved, error) in
            
            if saved {
                let fetchOptions = PHFetchOptions()
                fetchOptions.sortDescriptors = [NSSortDescriptor(key: "creationDate", ascending: true)]
                
                if let fetchResult = PHAsset.fetchAssets(with: .video, options: fetchOptions).lastObject {
                    self.openVideoInInstagram(fetchResult: fetchResult)
                }
            } else {
                UIAlertController.showAlert(nil, message: L10n.unableToShareVideoMessage, inViewController: fromViewController)
            }
        })
    }
    
    func openVideoInInstagram(fetchResult:PHAsset){
        if let instagramURL = URL(string: Constants.Exercises.InstagramSharedApplicationURL + fetchResult.localIdentifier) {
            if UIApplication.shared.canOpenURL(instagramURL) {
                UIApplication.shared.open(instagramURL, options: [:], completionHandler: nil)
            }
        }
    }
    
    func submitExercisesToServerFromViewController(viewController:ExercisesReportViewController, exerciseScore:ExerciseScore){
        
        guard let exerciseCategory = self.exerciseCategory, let exerciseTestFormat = self.exerciseTestFormat else{
            return
        }
        
        var scoreForServer:Int
        
        switch exerciseCategory {
        case .MileRun, .FortyYardDash:
            
            let minutes = exerciseScore.minutes ?? 0
            let seconds = exerciseScore.seconds ?? 0
            let milliseconds = exerciseScore.milliseconds ?? 0
            // miliseconds are entered as a decimal by user, for isntance, 4.87 seconds is really 4 seconds and 870 miliseconds, hence mulitplying milliseconds by 10 here
            scoreForServer = (minutes*60*1000) + (seconds*1000) + (milliseconds * 10)
        default:
            guard let reps = exerciseScore.reps else{
                return
            }
            scoreForServer = reps
        }
        NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
        self.exercisesDataProvider.submitExercise(exercise: exerciseCategory.rawValue, testFormat: exerciseTestFormat.rawValue, score: scoreForServer, vimeoID: self.exerciseVimeoID, completion: { (exerciseResult, errorMsg) in
            NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
            viewController.submitScoreButton?.setEnabled(enabled: true)
            if let exerciseResult = exerciseResult {
                self.setReportCardAndCreditsNeedsUpdate?()
                var viewData:SubmissionResultsViewData = SubmissionResultsViewData(exerciseCategory: exerciseCategory, exerciseTestFormat: exerciseTestFormat, exerciseResult: exerciseResult, exerciseScore: exerciseScore, videoExists: false)
                if self.videoURL != nil {
                    viewData = SubmissionResultsViewData(exerciseCategory: exerciseCategory, exerciseTestFormat: exerciseTestFormat, exerciseResult: exerciseResult, exerciseScore: exerciseScore, videoExists: true)
                }

                // Because we have a cacheURL, we failed to upload to VIMEO, store the submission ID and CacheURL and Upload later.
                if let exerciseCacheURL = self.exerciseCacheURL {
                    let identifier = "\(exerciseCategory.rawValue).\(exerciseTestFormat.rawValue)"
                    let submission = CacheSubmission(videoURL: exerciseCacheURL, submissionID: exerciseResult.submissionId, videoIdentifier: identifier)
                    let cacheManager = CacheSubmissionManager()
                    cacheManager.saveSubmissions(saveSubmission: submission)
                }

                self.moveToSubmissionResults(submissionResultsViewData: viewData)
                self.exerciseCacheURL = nil
                self.exerciseVimeoID = nil
            } else {
                let errorMsg = errorMsg ?? L10n.unknownErrorMessage
                UIAlertController.showAlert("Submit To Server", message: errorMsg, inViewController: viewController)
            }
        })
    }
    
    @objc private func closeButtonTapped(_ sender:UIBarButtonItem){
        self.exercisesViewController.dismiss(animated: true, completion: nil)
    }
}

extension ExercisesCoordinator : UIImagePickerControllerDelegate, UINavigationControllerDelegate {
	
	func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
        let asset = retrieveVideo(media: info)
        self.videoURL = videoURL(media: info)
        
        self.navigationController.dismiss(animated: true, completion: {
            self.uploadVideoToVimeo(asset: asset)
        })
    }
    
    func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
        self.navigationController.dismiss(animated: true, completion: nil)
    }
    
    fileprivate func uploadVideoToVimeo(asset: AVURLAsset?) {
        if let asset = asset {
            let identifier = (self.exerciseCategory?.rawValue)! + "." + (self.exerciseTestFormat?.rawValue)!
            NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
            REPVimeoUploaderManager.sharedVideoManager.uploadToVimeo(asset: asset, identifier: identifier) { [weak self] (vimeoID, error) in
                NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
                
                guard let strongSelf = self else {
                    return
                }
                
                if error != nil {
                    let alertController = UIAlertController(title: "Error", message: "Video did not upload.", preferredStyle: .alert)
                    let ok = UIAlertAction(title: "Try Again", style: .default, handler: {(alert: UIAlertAction) in
                        self?.uploadVideoToVimeo(asset: asset)
                    })
                    let cancel = UIAlertAction(title: "Submit without video", style: .cancel, handler: {(alert: UIAlertAction) in
                        strongSelf.exerciseVimeoID = nil
                        strongSelf.moveToSubmission()
                    })
                    alertController.addAction(ok)
                    alertController.addAction(cancel)
                    strongSelf.navigationController.topViewController?.present(alertController, animated: true, completion: nil)
                }
                else {
                    strongSelf.exerciseVimeoID = vimeoID
                    strongSelf.moveToSubmission()
                }
            }
        } else {
            if let topViewController = self.navigationController.topViewController {
                UIAlertController.showAlert("Video Error", message: "Unable to retrieve video", inViewController: topViewController)
            }
        }
    }
    
    fileprivate func videoURL(media: [UIImagePickerController.InfoKey : Any]) -> URL? {
        guard let mediaType: String = media[.mediaType] as? String, mediaType == "public.movie", let mediaURL = media[.mediaURL] as? URL else {
                return nil
        }
		
        return mediaURL
    }
    
    fileprivate func retrieveVideo(media: [UIImagePickerController.InfoKey : Any]) -> AVURLAsset? {
        guard let mediaURL = videoURL(media: media) else {
            return nil
        }
        return AVURLAsset(url: mediaURL)
    }
}
