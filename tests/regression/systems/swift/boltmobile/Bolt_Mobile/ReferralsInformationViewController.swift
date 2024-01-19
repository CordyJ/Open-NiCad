//
//  ReferralsInformationViewController.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-20.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

enum ReferralsInformationPresentationStyle:Int {
    case present
    case push
}

struct ReferralsInformationViewControllerViewData {
    let presentationStyle:ReferralsInformationPresentationStyle
}

class ReferralsInformationViewController: UIViewController {
    
    @IBOutlet private var getStartedButton:UIButton?
    
    var dismiss:(()->())?
    var getStarted:(()->())?
    
    var viewData:ReferralsInformationViewControllerViewData?
    
    override func viewDidLoad() {
        configureView()
    }
    
    private func configureView(){
        if let viewData = viewData, viewData.presentationStyle == .present {
            getStartedButton?.isHidden = true
            navigationItem.rightBarButtonItem = UIBarButtonItem(barButtonSystemItem: .done, target: self, action: #selector(doneButtonTapped(_:)))
        }
    }
    
    @IBAction private func doneButtonTapped(_ sender:UIBarButtonItem?){
        dismiss?()
    }

    @IBAction private func getStartedTapped(_ sender:UIButton?){
        getStarted?()
    }

}
