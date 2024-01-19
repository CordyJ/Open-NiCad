//
//  ProfileCoordinator.swift
//  REPerformance
//
//  Created by Francis Chary on 2017-05-02.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import NVActivityIndicatorView


enum LifestyleQuizType:Int {
    case BasicInfo = 0
    case Nutrition = 1
    case LifeStyle = 2
    case Exercise = 3
}

class ProfileCoordinator {
    let navigationController: UINavigationController
	let profileDataProvider: ProfileDataProvider
    let profileViewController: ProfileViewController
    var profileLifeStyle: LifestyleType?
    let zero:NSNumber = 0 as NSNumber
    let lifestyleDataProvider:LifestyleDataProvider
    var profileNeedsSumission:Bool = false
    var userGender:String
    
    var profileCompletionChanged: (()->())?
    var logout: (()->())?
    var setReportCardNeedsUpdate: (()->())?
    var profileNotification: (()->())?
    var profileFilledOutFirstTime: (()->())?
    var genderChanged: (()->())?

    let challengesCoordinator = ChallengesCoordinator()

	init(dataProvider: ProfileDataProvider) {
        if let gender = UserDefaults.standard.userGender {
            userGender = gender
        } else {
            userGender = ""
        }
        self.navigationController = UINavigationController()
		self.profileDataProvider = dataProvider
        self.navigationController.title = L10n.profileTitle
        self.profileViewController = StoryboardScene.Profile.profileVC.instantiate()
		self.profileViewController.tabBarItem = UITabBarItem(title: L10n.profileTabBarItemTitle, image: #imageLiteral(resourceName: "TabBar_Profile"), tag: 0)
        self.navigationController.viewControllers = [profileViewController]
        self.lifestyleDataProvider = LifestyleDataProvider()
		self.setupProfileViewController()
		self.loadLifeStyle()
    }

    func tabBarViewController() -> UIViewController {
        return self.navigationController
    }
    
    private func setupProfileViewController() {
        self.profileViewController.profileWillAppear = {
            self.setProfileCreditsLabel()
            if self.profileNeedsSumission {
                self.setLifestyle()
            }
            CreditsUpdater.updateCredits { (success) in
                // this is called again, in case the credits have been updated.
                self.setProfileCreditsLabel()
            }
        }
        self.profileViewController.chooseProfile = { lifestyleQuizType in
            
            if lifestyleQuizType == .BasicInfo {
                let basicInfoProfileViewController = StoryboardScene.Profile.basicInfoQuestionnaireVC.instantiate()
                basicInfoProfileViewController.updateProfile = {basicInfoData in
                    self.lifestyleDataProvider.saveBasicInfoData(basicInfoData)
                    let units = self.lifestyleDataProvider.checkUnitsComplete(basicInfoQuestionnaire: basicInfoData)
                    if !units.weightComplete {
                        UIAlertController.showAlert(nil, message: L10n.weightCheckboxLeftBlank, inViewController: self.profileViewController)
                    } else if !units.heightComplete {
                        UIAlertController.showAlert(nil, message: L10n.heightCheckboxLeftBlank, inViewController: self.profileViewController)
                    }
                    if let gender = UserDefaults.standard.userGender {
                        if gender != self.userGender{
                            self.userGender = gender
                            self.genderChanged?()
                        }
                    }
                    self.setLifestyle()
                }
                basicInfoProfileViewController.dismiss = {
                    self.navigationController.popViewController(animated: true)
                }
                basicInfoProfileViewController.locationCell = { locationDisplay in
                    let locationSearchViewController = StoryboardScene.Profile.locationSearchVC.instantiate()
                    locationSearchViewController.dismiss = {
                        locationSearchViewController.dismiss(animated: true, completion: nil)
                    }
                    
                    locationSearchViewController.selectedCountry = { countryID in
                        for index in basicInfoProfileViewController.internalData.singleValueQuestions.indices{
                            if basicInfoProfileViewController.basicInfoData?.singleValueQuestions[index].index == Constants.Profile.BasicInfoCountryQuestionIndex{
                                basicInfoProfileViewController.basicInfoData = self.lifestyleDataProvider.loadBasicInfoData()
                                if basicInfoProfileViewController.basicInfoData?.singleValueQuestions[index].valueAnswer.value != countryID{
                                    basicInfoProfileViewController.basicInfoData?.singleValueQuestions[index].valueAnswer.value = countryID
                                    for index in basicInfoProfileViewController.internalData.singleValueQuestions.indices{
                                        if basicInfoProfileViewController.basicInfoData?.singleValueQuestions[index].index == Constants.Profile.BasicInfoProvinceQuestionIndex{
                                            basicInfoProfileViewController.basicInfoData?.singleValueQuestions[index].valueAnswer.value = ""
                                            break
                                        }
                                    }
                                }
                                break
                            }
                            basicInfoProfileViewController.tableView?.reloadData()
                        }
                        if locationSearchViewController.searchController.isActive {
                            locationSearchViewController.searchController.dismiss(animated: true, completion: {
                            })
                        }
                        locationSearchViewController.dismiss(animated: true, completion: nil)
                    }
                
                    locationSearchViewController.selectedProvince = { provinceID in
                        for index in basicInfoProfileViewController.internalData.singleValueQuestions.indices{
                            if basicInfoProfileViewController.basicInfoData?.singleValueQuestions[index].index == Constants.Profile.BasicInfoProvinceQuestionIndex{
                                basicInfoProfileViewController.basicInfoData = self.lifestyleDataProvider.loadBasicInfoData()
                                basicInfoProfileViewController.basicInfoData?.singleValueQuestions[index].valueAnswer.value = provinceID
                                basicInfoProfileViewController.tableView?.reloadData()
                            }
                        }
                        if locationSearchViewController.searchController.isActive{
                            locationSearchViewController.searchController.dismiss(animated: true, completion: { 
                                locationSearchViewController.dismiss(animated: true, completion: nil)
                            })
                        }
                        locationSearchViewController.dismiss(animated: true, completion: nil)
                    }
                    
                    guard let locations:Locations = LocationsDataProvider.loadLoactionsFromFile() else {
                        UIAlertController.showAlert(nil, message: "There was an error loading the list of locations", inViewController: basicInfoProfileViewController)
                        return
                    }
                    
                    var viewData:LocationsSearchViewData?
                    var currentCountryID:String? = ""
                    var currentProvinceID:String? = ""
                    for question in basicInfoProfileViewController.internalData.singleValueQuestions{
                        if question.index == Constants.Profile.BasicInfoCountryQuestionIndex{
                            currentCountryID = question.valueAnswer.value
                        }
                        if question.index == Constants.Profile.BasicInfoProvinceQuestionIndex{
                            currentProvinceID = question.valueAnswer.value
                        }
                    }
                    switch locationDisplay{
                    case .Country:
                        viewData = LocationsSearchViewData(locationDisplay: locationDisplay, locations: locations, countryID: currentCountryID, provinceID:nil)
                    case .Province:
                        
                        if currentCountryID == "" || currentCountryID == nil{
                            UIAlertController.showAlert(nil, message: "Please select a country before selecting a province", inViewController: basicInfoProfileViewController)
                            return
                        } else {
                            viewData = LocationsSearchViewData(locationDisplay: locationDisplay, locations: locations, countryID: currentCountryID, provinceID:currentProvinceID)
                        }
                    }
                    
                    locationSearchViewController.viewData = viewData
                    
                    let enclosingNav = UINavigationController(rootViewController: locationSearchViewController)
                    self.navigationController.present(enclosingNav, animated: true, completion: nil)
                }
                basicInfoProfileViewController.basicInfoData = self.lifestyleDataProvider.loadBasicInfoData()
                basicInfoProfileViewController.locations = LocationsDataProvider.loadLoactionsFromFile()
                self.navigationController.pushViewController(basicInfoProfileViewController, animated: true)
            } else {
                let baseProfileViewController = StoryboardScene.Profile.questionnaireVC.instantiate()
                baseProfileViewController.updateProfile = {lifestyleQuizType, questionnaireData in
                    self.lifestyleDataProvider.saveQuestionnaireData(questionnaireData, lifestyleQuizType: lifestyleQuizType)
                    self.setLifestyle()
                }
                baseProfileViewController.dismiss = {
                    self.navigationController.popViewController(animated: true)
                }
                baseProfileViewController.questionnaireData = self.lifestyleDataProvider.loadQuestionnaireData(lifestyleQuizType: lifestyleQuizType)
                baseProfileViewController.lifestyleQuizType = lifestyleQuizType
                self.navigationController.pushViewController(baseProfileViewController, animated: true)
            }
        }
        self.profileViewController.showCompleteLifestyle = { lifestyleQuizType in
            switch lifestyleQuizType {
            case .BasicInfo:
                return self.lifestyleDataProvider.basicInfoQuizComplete()
            case .Nutrition, .LifeStyle, .Exercise:
                if (self.lifestyleDataProvider.totalPointsForLifestyleQuizType(lifestyleQuizType) != nil){
                    return true
                } else {
                    return false
                }
            }
        }
		
		self.profileViewController.showAchievements = {
			let achievementsViewController = StoryboardScene.Profile.achievementsViewControllerStoryboardIdentifier.instantiate()
			achievementsViewController.navigationItem.leftBarButtonItem = UIBarButtonItem(title: L10n.doneBarItemTitle, style: .plain, target: self, action: #selector(self.doneButtonTapped))
			achievementsViewController.navigationItem.title = "Achievements"
			let navigationController = UINavigationController(rootViewController: achievementsViewController)
			self.navigationController.present(navigationController, animated: true, completion: nil)
		}
        
        self.profileViewController.showOurValue = {
            let ourValueCoordinator = OurValueCoordinator()
            let vc = ourValueCoordinator.rootViewController()
            vc.navigationItem.leftBarButtonItem = UIBarButtonItem(title: L10n.doneBarItemTitle, style: .plain, target: self, action: #selector(self.doneButtonTapped))
            let navigationController = UINavigationController(rootViewController: vc)
            self.navigationController.present(navigationController, animated: true, completion: nil)
        }
        
        self.profileViewController.logout = {
            self.logout?()
        }
        
        self.profileViewController.onChallengesPressed = {
            let vc = self.challengesCoordinator.rootViewController()
            vc.navigationItem.leftBarButtonItem = UIBarButtonItem(image: Asset.Assets.xIcon.image, style: .plain, target: self, action: #selector(self.doneButtonTapped))
            let navigationController = UINavigationController(rootViewController: vc)
            self.navigationController.present(navigationController, animated: true, completion: nil)
        }
    }
	
	@IBAction func doneButtonTapped(_ : Any) {
		self.profileViewController.dismiss(animated: true, completion: nil)
	}
    
    private func setLifestyle()
    {
		guard
			let totalPoints = lifestyleDataProvider.sumAllPoints(),
			let gender = UserDefaults.standard.userGender,
			let weight = UserDefaults.standard.userWeight,
			let age = UserDefaults.standard.userAge,
			let countryID = lifestyleDataProvider.getCountryID(),
			let provinceID = lifestyleDataProvider.getProvinceID()
			else {
				saveLifestyle()
				return
		}
		
        let lifestyleType:LifestyleType = getLifestyleTypeWithPoints(totalPoints)
		submitProfileToServerFromViewController(viewController: self.profileViewController, lifestyleType: lifestyleType, gender: gender, weight: weight, age: age, countryID: countryID, provinceID: provinceID) { (success) in
            if success{
                self.profileNeedsSumission = false
                self.saveLifestyle()
                if let profileNeverFilledOut = UserDefaults.standard.profileNeverFilledOut {
                    if profileNeverFilledOut {
                        UserDefaults.standard.profileNeverFilledOut = false
                        self.profileFilledOutFirstTime?()
                    }
                }
            } else {
                self.profileNeedsSumission = true
            }
        }
    }
    
    private func setProfileCreditsLabel(){
        if let userCredits = UserDefaults.standard.userCredits {
            profileViewController.totalCreditsText  = String(format: "%@: %@", L10n.totalCredits, userCredits)
        } else {
            profileViewController.totalCreditsText  = L10n.errorLoadingCredits
        }
        if let dollars = UserDefaults.standard.userDollars {
            profileViewController.totalDollarsText = String(format: "%@: $%.2f", L10n.dollarValue, dollars)
        } else {
            profileViewController.totalDollarsText = ""
        }
        profileViewController.setCreditsLabel()
    }
    
    func loadLifeStyle(){
        var lifestyleType:LifestyleType?
        if let totalPoints = lifestyleDataProvider.sumAllPoints() {
            if lifestyleDataProvider.basicInfoQuizComplete(){
                UserDefaults.standard.profileIsComplete = true
                lifestyleType = getLifestyleTypeWithPoints(totalPoints)
            } else {
                UserDefaults.standard.profileIsComplete = false
                lifestyleType = nil
            }
        } else {
            UserDefaults.standard.profileIsComplete = false
            lifestyleType = nil
        }
        self.profileLifeStyle = lifestyleType
        self.profileViewController.lifestyleType = self.profileLifeStyle
        self.profileViewController.loadLifestyle()
        setLifestyleTypeToUserDefaults(lifestyleType: lifestyleType)
        setReportCardNeedsUpdate?()
        self.profileCompletionChanged?()
    }
    
    private func saveLifestyle(){
        self.profileNotification?()
        loadLifeStyle()
    }
    
    private func setLifestyleTypeToUserDefaults(lifestyleType:LifestyleType?){
        guard let type = lifestyleType else {
            UserDefaults.standard.lifestyleType = ""
            return
        }
        UserDefaults.standard.lifestyleType = type.rawValue
    }
    
    private func getLifestyleTypeWithPoints(_ totalPoints:Int) -> LifestyleType {
        if totalPoints <= Constants.Profile.LifestyleActionCeiling {
            return .Action
        } else if totalPoints > Constants.Profile.LifestyleActionCeiling && totalPoints <= Constants.Profile.LifestyleFitCeiling {
            return .Fit
        } else if totalPoints > Constants.Profile.LifestyleFitCeiling && totalPoints <= Constants.Profile.LifestyleAthleteCeiling {
            return .Athlete
        } else if totalPoints > Constants.Profile.LifestyleAthleteCeiling {
            return .Elite
        } else {
            return .Action
        }
    }
	
	/// Attempts to submit the profile (if completed) in the background.
	/// On submission failure, will mark the profile to be submitted the next time the profile tab is loaded.
	func silentlySubmitProfile() {
		if let profileNeverFilledOut = UserDefaults.standard.profileNeverFilledOut, profileNeverFilledOut == true {
			return
		}
		
		guard
			let totalPoints = lifestyleDataProvider.sumAllPoints(),
			let gender = UserDefaults.standard.userGender,
			let weight = UserDefaults.standard.userWeight,
			let age = UserDefaults.standard.userAge,
			let countryID = lifestyleDataProvider.getCountryID(),
			let provinceID = lifestyleDataProvider.getProvinceID()
			else {
				return
		}
		
		let lifestyleType = getLifestyleTypeWithPoints(totalPoints)
		self.submitProfileToServerFromViewController(viewController: self.profileViewController, lifestyleType: lifestyleType, gender: gender, weight: weight, age: age, countryID: countryID, provinceID: provinceID) { (success) in
			if !success {
				self.profileNeedsSumission = true
			}
		}
	}
	
	
	//MARK: Server Submission
	
	func submitProfileToServerFromViewController(viewController: ProfileViewController, lifestyleType: LifestyleType, gender: String, weight: Int, age: Int, countryID: String, provinceID: String, completion: @escaping (Bool)->()) {
		NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
		profileDataProvider.submitProfile(lifestyle: lifestyleType, gender: gender, weight: weight, age: age, countryCode: countryID, regionCode: provinceID) { (success, errorMessage) in
			NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
			if success {
				completion(success)
			} else {
				let errorMessage = errorMessage ?? L10n.unknownErrorMessage
				UIAlertController.showAlert("Submit to Server", message: errorMessage, inViewController: viewController)
				completion(false)
			}
		}
	}
}
