//
//  LifestyleTutorialViewController.swift
//
//  Created by Alan Yeung on 2017-04-26.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

enum LifestyleType: String {
    case Action = "Action"
    case Fit = "Fit"
    case Athlete = "Athlete"
    case Elite = "Elite"
    
    func image() -> UIImage {
        switch self {
        case .Action:
            return Asset.Assets.Profile.actionProfile.image
        case .Fit:
            return Asset.Assets.Profile.fitProfile.image
        case .Athlete:
            return Asset.Assets.Profile.athleteProfile.image
        case .Elite:
            return Asset.Assets.Profile.eliteProfile.image
        }
    }
}


class LifestyleTutorialViewController: UIViewController {
	
	override var preferredStatusBarStyle: UIStatusBarStyle {
		return .lightContent
	}

    @IBOutlet fileprivate var subtitleLabel: UILabel?
    
    var selectedLifestyleType: ((LifestyleType)->())?
    var exit: (()->())?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        self.title = L10n.lifestyleTutorialTitle
        self.subtitleLabel?.text = L10n.lifestyleTutorialSubtitle
    }

    // MARK: - IBActions
    
    @IBAction fileprivate func actionTutorial(_ sender:UIButton) {
        selectedLifestyleType?(.Action)
    }
    
    @IBAction fileprivate func fitTutorial(_ sender:UIButton) {
        selectedLifestyleType?(.Fit)
    }
    
    @IBAction fileprivate func athleteTutorial(_ sender:UIButton) {
        selectedLifestyleType?(.Athlete)
    }
    
    @IBAction fileprivate func eliteTutorial(_ sender:UIButton) {
        selectedLifestyleType?(.Elite)
    }
    
    @IBAction fileprivate func okayTapped(_ sender: UIButton) {
        exit?()
    }
}
