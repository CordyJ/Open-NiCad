//
//  ProfileViewController.swift
//
//  Created by Alan Yeung on 2017-04-27.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class ProfileViewController: UIViewController {
	
	override var preferredStatusBarStyle: UIStatusBarStyle {
		return .lightContent
	}

    @IBOutlet fileprivate var lifestyleContainerView: UIView?
    @IBOutlet fileprivate var lifestyleLabel: UILabel?
    @IBOutlet fileprivate var lifestyleImage: UIImageView?
    @IBOutlet fileprivate var lifestyleCheck: UIImageView?
    
    @IBOutlet private var basicInfoCheckmark:UIImageView?
    @IBOutlet private var nutritionCheckmark:UIImageView?
    @IBOutlet private var lifestyleCheckmark:UIImageView?
    @IBOutlet private var exerciseCheckmark:UIImageView?
    
    @IBOutlet private var logoutImageView: UIImageView?
    @IBOutlet private var logoutTitle: UILabel?
    @IBOutlet private var logoutButton: UIButton?
    
    @IBOutlet private var totalCreditsLabel: UILabel?
    @IBOutlet weak var totalDollarsLabel: UILabel!
    
    @IBOutlet private var challengesButton: UIButton?

    var lifestyleType: LifestyleType?
    var totalCreditsText:String = "Total Credits:"
    var totalDollarsText:String = ""
    var chooseProfile: ((LifestyleQuizType)->())?
    var showCompleteLifestyle: ((_ lifestyleQuizType:LifestyleQuizType)->(Bool))?
	var showAchievements: (()->())?
    var showOurValue: (()->())?
    var logout: (()->())?
    var profileWillAppear: (()->())?
    var onChallengesPressed: (()->())?
    
    override var prefersStatusBarHidden : Bool {
        return true
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setUpView()
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        loadLifestyle()
        self.tabBarController?.navigationItem.title = L10n.profileTitle
        profileWillAppear?()
        setCreditsLabel()
    }
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        REPAnalytics.trackScreenWithName(screenName: ScreenName.HomePage.Profile, className: String(describing: self))
    }
    
    func setUpView(){
        self.lifestyleContainerView?.addDashedBorder(strokeColor: UIColor.white, lineWidth: 2)
        self.challengesButton?.setTitle(L10n.challengeButtonTitle, for: .normal)
    }

    func loadLifestyle() {
        guard let lifestyleType = lifestyleType else {
            self.lifestyleContainerView?.isHidden = false
            self.lifestyleCheck?.image = Asset.Assets.Profile.whiteCheckCircle.image
            self.lifestyleLabel?.text = "N/A"
            self.lifestyleImage?.image = nil
            showCompletedQuestionnaire()
            return
        }
        self.lifestyleContainerView?.isHidden = true
        self.lifestyleCheck?.image = Asset.Assets.checkYellow.image
        self.lifestyleLabel?.text = lifestyleType.rawValue
        self.lifestyleImage?.image = lifestyleType.image()
        showCompletedQuestionnaire()
    }
    
    func setCreditsLabel(){
        totalCreditsLabel?.text = totalCreditsText
        totalDollarsLabel?.text = totalDollarsText
    }
    
    func showCompletedQuestionnaire(){
        guard let basicInfoComplete = showCompleteLifestyle?(.BasicInfo) else {
            return
        }
        if basicInfoComplete{
            basicInfoCheckmark?.isHidden = false
        } else {
            basicInfoCheckmark?.isHidden = true
        }
        
        guard let nutritionComplete = showCompleteLifestyle?(.Nutrition) else {
            return
        }
        if nutritionComplete{
            nutritionCheckmark?.isHidden = false
        } else {
            nutritionCheckmark?.isHidden = true
        }
        
        guard let lifestyleComplete = showCompleteLifestyle?(.LifeStyle) else {
            return
        }
        if lifestyleComplete{
            lifestyleCheckmark?.isHidden = false
        } else {
            lifestyleCheckmark?.isHidden = true
        }
        
        guard let exerciseComplete = showCompleteLifestyle?(.Exercise) else {
            return
        }
        if exerciseComplete{
            exerciseCheckmark?.isHidden = false
        } else {
            exerciseCheckmark?.isHidden = true
        }
        
    }
    
    @IBAction fileprivate func basicInfoTapped() {
        chooseProfile?(.BasicInfo)
    }
    
    @IBAction fileprivate func nutritionTapped() {
        chooseProfile?(.Nutrition)
    }
    
    @IBAction fileprivate func lifestyleTapped() {
        chooseProfile?(.LifeStyle)
    }

    @IBAction fileprivate func exerciseTapped() {
        chooseProfile?(.Exercise)
	}
	
	@IBAction fileprivate func achievementsTapped() {
		showAchievements?()
	}
    
    @IBAction fileprivate func ourValueTapped() {
        showOurValue?()
    }
    
    @IBAction private func logoutTapped(_ sender:UIButton){
        logout?()
    }
    
    @IBAction private func challengesPressed(_ sender: UIButton) {
        onChallengesPressed?()
    }
}
