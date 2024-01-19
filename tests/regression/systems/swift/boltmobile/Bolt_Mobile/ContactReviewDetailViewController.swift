//
//  ContactReviewDetailViewController.swift
//  Bolt Mobile
//
//  Created by Alan Yeung on 2017-09-20.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

class ContactReviewDetailViewController: UIViewController {
    
    @IBOutlet private var locationImageView:UIImageView?
    @IBOutlet private var addressLabel:UILabel?
    @IBOutlet private var phoneButton:UIButton?
    @IBOutlet private var internetButton:UIButton?
    @IBOutlet private var emailButton:UIButton?
    
    var didLoad:(()->())?
    var hours:(()->())?
    var phoneLocation:(()->())?
    var goToWebsite:(()->())?
    var emailLocation:(()->())?
    var reviewFacebook:(()->())?
    var reviewGoogle:(()->())?
    
    //The client changed their mind on this so the button has been removed from storyboard. Leave the code here in case they decide they want it in the future.
    var getDirections:(()->())?

    override func viewDidLoad() {
        super.viewDidLoad()
        didLoad?()
    }
    
    func configureView(storeLocation:StoreLocation){
        locationImageView?.image = UIImage(named: storeLocation.picture)
        addressLabel?.text = storeLocation.address
        phoneButton?.setTitle(storeLocation.phone, for: .normal)
        internetButton?.setTitle(storeLocation.website, for: .normal)
        emailButton?.setTitle(storeLocation.email, for: .normal)
    }
    
    @IBAction private func hoursTapped(_ sender:UIButton?){
        hours?()
    }
    
    @IBAction private func phoneCallTapped(_ sender:UIButton?){
        phoneLocation?()
    }
    
    @IBAction private func websiteTapped(_ sender:UIButton?){
        goToWebsite?()
    }
    
    @IBAction private func emailTapped(_ sender:UIButton?){
        emailLocation?()
    }
    
    @IBAction private func facebookReviewTapped(_ sender:UIButton?){
        reviewFacebook?()
    }
    
    @IBAction private func googleReviewTapped(_ sender:UIButton?){
        reviewGoogle?()
    }
    
    //The client changed their mind on this so the button has been removed from storyboard. Leave the code here in case they decide they want it in the future.
    @IBAction private func getDirectionsTapped(_ sender:UIButton?){
        getDirections?()
    }

}
