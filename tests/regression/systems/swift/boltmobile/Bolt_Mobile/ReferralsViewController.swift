//
//  ReferralsViewController.swift
//  Bolt Mobile
//
//  Created by Christopher Darc on 2017-09-20.
//  Copyright © 2017 Push Interactions. All rights reserved.
//

import UIKit

class ReferralsViewController: UIViewController {
    
    @IBOutlet private var balanceLabel:UILabel?
    @IBOutlet private var divider:UIView? {
        didSet {
            divider?.backgroundColor = UIColor(named: .boltMobileDarkBlue)
        }
    }
    
    var viewInfo:(()->())?
    var newReferral:(()->())?
    var redeem:(()->())?
    var editInfo:(()->())?
    
    var didAppear:(()->())?
    
    override func viewDidLoad() {
        navigationItem.rightBarButtonItem = UIBarButtonItem(image: Asset.infoBarButton.image, style: .plain, target: self, action: #selector(infoBarButtonTapped(_:)))
    }
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        didAppear?()
    }
    
    func setBalance(balance:String){
        balanceLabel?.text = balance
    }
    
    @IBAction private func infoBarButtonTapped(_ sender:UIButton?){
        viewInfo?()
    }
    
    @IBAction private func newReferralTapped(_ sender:UIButton?){
        newReferral?()
    }
    
    @IBAction private func redeemMyBoltbucks(_ sender:UIButton?){
        redeem?()
    }
    
    @IBAction private func editMyInfoTapped(_ sender:UIButton?){
        editInfo?()
    }

}
