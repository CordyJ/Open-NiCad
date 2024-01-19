//
//  ReportCardViewController.swift
//
//  Created by Alan Yeung on 2017-05-01.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import AVKit
import Photos


class ReportCardViewController: UIViewController, UINavigationControllerDelegate {
	
	// MARK: Outlets
	
	@IBOutlet fileprivate var reportCardTableView: UITableView?
	
	
	// MARK: - Properties
	
	override var preferredStatusBarStyle: UIStatusBarStyle {
		return .lightContent
	}
	
	var isPublic: Bool = false {
		didSet {
			self.reportCardTableView?.reloadData()
		}
	}
	
	var hasUnreadMessages: Bool = false {
		didSet {
			self.reportCardTableView?.reloadData()
		}
	}
	
	var profileImage: UIImage? {
		didSet {
			self.reportCardTableView?.reloadData()
		}
	}
	
	var name: String? {
		didSet {
			self.reportCardTableView?.reloadData()
		}
	}
	
	var age: Int? {
		didSet {
			self.reportCardTableView?.reloadData()
		}
	}
	
	var weight: Int? {
		didSet {
			self.reportCardTableView?.reloadData()
		}
	}
	
	var isMale: Bool = false {
		didSet {
			self.reportCardTableView?.reloadData()
		}
	}
	
	var lifestyleCategoryName: String? {
		didSet {
			self.reportCardTableView?.reloadData()
		}
	}
	
	var reportCard: ReportCard? {
		didSet {
			self.reportCardTableView?.reloadData()
		}
	}
	
	var isPersonalReportCard: Bool = true {
		didSet {
			self.reportCardTableView?.reloadData()
		}
	}
	
	var exerciseScores: ReportCardExerciseScores? {
		didSet {
			if let exerciseScores = self.exerciseScores {
				self.exerciseScoresViewModel = exerciseScores.generateExerciseScoresViewModel()
			}
			else {
				self.exerciseScoresViewModel = nil
			}
		}
	}
	
	fileprivate var exerciseScoresViewModel: [(ExerciseInfo, [ExerciseScoreAthleteCellViewModel])]? {
		didSet {
			if let exerciseScoresViewModel = self.exerciseScoresViewModel {
				var flattenedViewModel = [Any]()
				for exerciseScoresViewModelTuple in exerciseScoresViewModel {
					flattenedViewModel.append(exerciseScoresViewModelTuple.0)
					for exerciseScoreAthleteCellViewModel in exerciseScoresViewModelTuple.1 {
						flattenedViewModel.append(exerciseScoreAthleteCellViewModel)
					}
				}
				self.exerciseScoresViewModelCompact = flattenedViewModel
			}
			else {
				self.exerciseScoresViewModelCompact = nil
			}
		}
	}
	
	fileprivate var exerciseScoresViewModelCompact: [Any]? {
		didSet {
			self.reportCardTableView?.reloadData()
		}
	}
	
	
	// MARK: Closures
	
	var reportCardWillAppear: (()->())?
	var chat: (()->())?
	var shareReport: ((UIImage)->())?
	var changeProfileVisibility: ((Bool)->())?
    var updateProfileImage: ((UIImage)->())?
	var onMyLatestScoresPressed: (()->())?
	var onMyBestScoresPressed: (()->())?
	var onChallengesPressed: (()->())?
    	
	
	// MARK: - UIViewController Methods
    
    override func viewDidLoad() {
        super.viewDidLoad()
    }
	
	override func viewWillAppear(_ animated: Bool) {
		super.viewWillAppear(animated)
		
		self.reportCardWillAppear?()
	}
	
	override func viewDidAppear(_ animated: Bool) {
		super.viewDidAppear(animated)
		
		REPAnalytics.trackScreenWithName(screenName: ScreenName.HomePage.ReportCard, className: String(describing: self))
	}
    
    // Mark: UIImagePicker methods
    func checkCameraStatus() {
        if AVCaptureDevice.authorizationStatus(for: .video) ==  .authorized {
    
            // Already Authorized
            openCamera()
    
        } else if (AVCaptureDevice.authorizationStatus(for: .video) == .denied) ||
            (AVCaptureDevice.authorizationStatus(for: .video) == .restricted) {
    
            // Already Denied
            self.openDeniedCameraPermission()
    
        } else {
            AVCaptureDevice.requestAccess(for: .video,
                                          completionHandler: { (granted: Bool) in
                                            if granted == true {
                                                // User granted
                                                self.openCamera()
    
                                            } else {
                                                // User rejected
                                                print("camera restricted")
                                            }
            })
        }
    }
    
    func openDeniedCameraPermission() {
        
        AVCaptureDevice.requestAccess(for: AVMediaType.video) {(_ status: Bool) -> Void in
            if status != true {
                let accessDescription = Bundle.main.object(forInfoDictionaryKey: "NSCameraUsageDescription") as? String
                
                let alertController = UIAlertController(title: accessDescription, message:L10n.cameraPermission, preferredStyle: .alert)
                let cancelAction = UIAlertAction(title: L10n.cancel, style: .cancel, handler: nil)
                alertController.addAction(cancelAction)
                let settingsAction = UIAlertAction(title: L10n.goToSettings, style: .default, handler: {(_ action: UIAlertAction) -> Void in
                    UIApplication.shared.open((URL(string: UIApplication.openSettingsURLString)!), options: [:], completionHandler: nil)
                })
                alertController.addAction(settingsAction)
                self.present(alertController, animated: true, completion: nil)
            }
        }
    }
    
    func openCamera()
    {
        
        if UIImagePickerController.isSourceTypeAvailable(UIImagePickerController.SourceType.camera) {
            let imagePicker = UIImagePickerController()
            imagePicker.delegate = self
            imagePicker.allowsEditing = false
            imagePicker.navigationBar.tintColor = .black
            imagePicker.navigationBar.titleTextAttributes = nil
            imagePicker.navigationBar.isTranslucent = false
            imagePicker.sourceType = UIImagePickerController.SourceType.camera
            self.present(imagePicker, animated: true, completion: nil)
        }
        else
        {
            let alert  = UIAlertController(title: L10n.warning, message: L10n.cameraPermission, preferredStyle: .alert)
            alert.addAction(UIAlertAction(title: L10n.ok, style: .default, handler: nil))
            self.present(alert, animated: true, completion: nil)
        }
    }
    
    func checkGalleryStatus() {
        
        let status = PHPhotoLibrary.authorizationStatus()
        switch status {
        case .authorized:
            //handle authorized status
            openGallery ()
            
        case .denied, .restricted :
            //handle denied status
            handleDeniedLibraryPermission()
            
        case .notDetermined:
            // ask for permissions
            PHPhotoLibrary.requestAuthorization() { status in
                switch status {
                case .authorized:
                    self.openGallery()
                    
                case .denied, .restricted:
                    print("gallery restricted")
                    
                case .notDetermined:
                    break
                }
            }
        }
    }
    
    func handleDeniedLibraryPermission() {
        
        PHPhotoLibrary.requestAuthorization({(_ status: PHAuthorizationStatus) -> Void in
            if status != .authorized {
                let accessDescription = Bundle.main.object(forInfoDictionaryKey: "NSPhotoLibraryUsageDescription") as? String
                let alertController = UIAlertController(title: accessDescription, message:L10n.imagePermission, preferredStyle: .alert)
                let cancelAction = UIAlertAction(title: L10n.cancel, style: .cancel, handler: nil)
                alertController.addAction(cancelAction)
                let settingsAction = UIAlertAction(title: "Go to Settings", style: .default, handler: {(_ action: UIAlertAction) -> Void in
                    UIApplication.shared.open((URL(string: UIApplication.openSettingsURLString)!), options: [:], completionHandler: nil)
                })
                alertController.addAction(settingsAction)
                self.present(alertController, animated: true, completion: nil)
            }
        })
    }
    
    func openGallery()
    {
        if UIImagePickerController.isSourceTypeAvailable(UIImagePickerController.SourceType.photoLibrary){
            let imagePicker = UIImagePickerController()
            imagePicker.delegate = self
            imagePicker.allowsEditing = false
            imagePicker.navigationBar.tintColor = .black
            imagePicker.navigationBar.titleTextAttributes = nil
            imagePicker.navigationBar.isTranslucent = false
            imagePicker.sourceType = .photoLibrary
            self.present(imagePicker, animated: true, completion: nil)
        }
        else
        {
            let alert  = UIAlertController(title: L10n.warning, message: L10n.imagePermission, preferredStyle: .alert)
            alert.addAction(UIAlertAction(title: L10n.ok, style: .default, handler: nil))
            self.present(alert, animated: true, completion: nil)
        }
    }
}

extension ReportCardViewController: UIImagePickerControllerDelegate {
    func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
        self.profileImage = info[.originalImage] as? UIImage
        if let image = profileImage {
            self.updateProfileImage?(image)
        }
        picker.dismiss(animated: true, completion: nil)
    }
}

extension ReportCardViewController: UITableViewDataSource, UITableViewDelegate {
	
	func numberOfSections(in tableView: UITableView) -> Int {
		/*
		0 = Report Card
		1 = Scores
		2 = Options
		*/
		return 3
	}
	
	func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
		if section == 0 {
			return 3
		}
		else if section == 1 {
			guard let exerciseScoresViewModelCompact = self.exerciseScoresViewModelCompact else {
				return 0
			}
			
			return exerciseScoresViewModelCompact.count + 1
		}
		else if section == 2 {
			return self.isPersonalReportCard == true ? 1 : 0
		}
		else {
			fatalError()
		}
	}
	
	func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
		if indexPath.section == 0 {
			if indexPath.row == 0 {
				let cell = tableView.dequeueReusableCell(withIdentifier: "Personal Info Cell Identifier", for: indexPath) as! ReportCardPersonalInfoTableViewCell
				cell.isPersonal = self.isPersonalReportCard
				cell.hasUnreadMessages = (self.hasUnreadMessages && self.isPersonalReportCard)
				cell.profileImage = self.profileImage
				cell.name = self.name
				cell.age = self.age
				cell.weight = self.weight
				cell.lifestyleCategoryName = self.lifestyleCategoryName
				cell.chat = { [unowned self] in
					self.chat?()
				}
                
				cell.shareReport = { [unowned self] in
					guard let reportCardCell = tableView.cellForRow(at: IndexPath(row: 1, section: 0)) as? ReportCardScoreBreakdownTableViewCell, let reportCardSnapshot = reportCardCell.createReportCard() else {
						return
					}
					
					self.shareReport?(reportCardSnapshot)
				}
				
				return cell
			}
			else if indexPath.row == 1 {
				let cell = tableView.dequeueReusableCell(withIdentifier: "Report Card Cell Identifier", for: indexPath) as! ReportCardScoreBreakdownTableViewCell
				cell.isPersonal = self.isPersonalReportCard
				cell.isMale = self.isMale
				cell.reportCard = self.reportCard
				cell.isPublic = self.isPublic
				cell.changeProfileVisibility = { [unowned self] (isPrivate) in
					self.changeProfileVisibility?(isPrivate)
				}
                cell.updateProfileImage = {
                    
                    let alert = UIAlertController(title: L10n.imageSource, message: nil, preferredStyle: .actionSheet)
                    alert.addAction(UIAlertAction(title: L10n.camera, style: .default, handler: { _ in
                        self.checkCameraStatus()
                    }))
                    
                    alert.addAction(UIAlertAction(title: L10n.gallery, style: .default, handler: { _ in
                        self.checkGalleryStatus()
                    }))
                    
                    alert.addAction(UIAlertAction.init(title: L10n.cancel, style: .cancel, handler: nil))
                    
                    self.present(alert, animated: true, completion: nil)
                }
				
				return cell
			}
			else if indexPath.row == 2 {
				let cell = tableView.dequeueReusableCell(withIdentifier: "Total Reps Volume Cell Identifier", for: indexPath) as! ReportCardTotalRepsVolumeTableViewCell
				cell.totalReps = self.reportCard?.totalReps
				cell.totalVolume = self.reportCard?.totalVolume
				
				return cell
			}
			else {
				fatalError()
			}
		}
		else if indexPath.section == 1 {
			if indexPath.row == 0 {
				let cell = tableView.dequeueReusableCell(withIdentifier: "Best Scores Cell Identifier", for: indexPath)
				
				return cell
			}
			else if let exerciseInfo = self.exerciseScoresViewModelCompact![(indexPath.row - 1)] as? ExerciseInfo {
				let cell = tableView.dequeueReusableCell(withIdentifier: "Score Section Header", for: indexPath) as! MyScoreSectionHeaderTableViewCell
				cell.configure(with: exerciseInfo)
				
				return cell
			}
			else if let exerciseScoreAthleteCellViewModel = self.exerciseScoresViewModelCompact![(indexPath.row - 1)] as? ExerciseScoreAthleteCellViewModel {
				let cell = tableView.dequeueReusableCell(withIdentifier: "Score Cell Identifier", for: indexPath) as! ExerciseScoreAthleteTableViewCell
				cell.configure(with: exerciseScoreAthleteCellViewModel)
				
				return cell
			}
			
			fatalError()
		}
		else if indexPath.section == 2 {
			let cell = tableView.dequeueReusableCell(withIdentifier: "Score Options Cell Identifier", for: indexPath) as! ReportCardScoreOptionsTableViewCell
			cell.viewLatestScores = { [unowned self] in
				self.onMyLatestScoresPressed?()
			}
			cell.viewBestScores = { [unowned self] in
				self.onMyBestScoresPressed?()
			}
			cell.viewChallenges = { [unowned self] in
				self.onChallengesPressed?()
			}
			
			return cell
		}
		else {
			fatalError()
		}
	}
    
}
