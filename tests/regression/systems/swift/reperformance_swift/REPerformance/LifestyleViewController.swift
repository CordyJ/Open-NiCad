//
//  LifestyleViewController.swift
//
//  Created by Alan Yeung on 2017-04-27.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

struct Lifestyle {
    let title: String
    let detail: String
    let backgroundImage: UIImage
}


class LifestyleViewController: UIViewController {

    @IBOutlet fileprivate var backgroundImageView: UIImageView?
    @IBOutlet fileprivate var titleLabel: UILabel?
    @IBOutlet fileprivate var detailLabel: UILabel?
    
    var lifestyle: Lifestyle?
    var exit: (()->())?

    override var prefersStatusBarHidden : Bool {
        return true
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        
        loadLifestyle(lifestyle: lifestyle)
    }
    
    fileprivate func loadLifestyle(lifestyle: Lifestyle?) {
        guard let lifestyle = lifestyle else {
            return
        }
        
        self.titleLabel?.text = lifestyle.title
        self.detailLabel?.text = lifestyle.detail
        self.backgroundImageView?.image = lifestyle.backgroundImage
    }
    
    // MARK: - IBActions
    
    @IBAction fileprivate func exitTapped(_ sender: UIButton) {
        exit?()
    }
}
