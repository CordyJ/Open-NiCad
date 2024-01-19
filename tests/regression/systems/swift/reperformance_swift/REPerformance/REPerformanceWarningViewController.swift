//
//  ExercisesProfileWarningViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-03.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class REPerformanceWarningViewController: UIViewController {
	
	override var preferredStatusBarStyle: UIStatusBarStyle {
		return .lightContent
	}
    
    @IBOutlet private var titleLabel: UILabel?
    @IBOutlet private var descriptionLabel: UILabel?
    @IBOutlet private var enclosingView: UIView?
    @IBOutlet private var okButton: UIButton?
    @IBOutlet private var cancelButton: UIButton?
    
    var ok: (()->())?
    var cancel: (()->())?

    override func viewDidLoad() {
        super.viewDidLoad()
        
        setUpView()
    }
    
    private func setUpView(){
        enclosingView?.layer.cornerRadius = Constants.UIConstants.CornerRadius
        enclosingView?.layer.masksToBounds = true
        
        titleLabel?.textColor = UIColor.init(named: .rePerformanceBlueText)
        descriptionLabel?.textColor = UIColor.init(named: .rePerformanceBlueText)
        
        okButton?.setUpBlueButton()
        cancelButton?.setUpBlueButton()
    }
    
    func configureView(titleText:String, descriptionText:String, okButtonVisible:Bool, cancelButtonVisible:Bool){
        self.titleLabel?.text = titleText
        self.descriptionLabel?.text = descriptionText
        self.okButton?.isHidden = !okButtonVisible
        self.cancelButton?.isHidden = !cancelButtonVisible
    }
    
    func setOkButtonTitleText(_ text:String){
        self.okButton?.setTitle(text, for: .normal)
    }
    
    @IBAction private func okTapped(_ sender: UIButton){
        ok?()
    }
    
    @IBAction private func cancelTapped(_ sender: UIButton){
        cancel?()
    }
}
