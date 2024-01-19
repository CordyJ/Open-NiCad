//
//  LearnAboutProViewController.swift
//  REPerformance
//
//  Created by Alan Yeung on 2017-05-25.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import WebKit

class LearnAboutProViewController: UIViewController {

    @IBOutlet fileprivate var headerLabel: UILabel!
    @IBOutlet fileprivate var leaderTitleLabel: UILabel!
    @IBOutlet fileprivate var leaderDetailLabel: UILabel!
    @IBOutlet fileprivate var friendsTitleLabel: UILabel!
    @IBOutlet fileprivate var friendsDetailLabel: UILabel!
    @IBOutlet fileprivate var dealsTitleLabel: UILabel!
    @IBOutlet fileprivate var dealsDetailLabel: UILabel!
    
    @IBOutlet fileprivate var leftContainerView: UIView!
    @IBOutlet fileprivate var rightContainerView: UIView!
    @IBOutlet fileprivate var exclusiveDealsContainerViewConstraint : NSLayoutConstraint!
    @IBOutlet fileprivate var leftIndicatorView: UIActivityIndicatorView!
    @IBOutlet fileprivate var rightIndicatorView: UIActivityIndicatorView!
    @IBOutlet fileprivate var leftTitleLabel: UILabel!
    @IBOutlet fileprivate var rightTitleLabel: UILabel!
    @IBOutlet fileprivate var leftDollarLabel: UILabel!
    @IBOutlet fileprivate var rightDollarLabel: UILabel!
    @IBOutlet fileprivate var leftGetButton: UIButton!
    @IBOutlet fileprivate var rightGetButton: UIButton!
    @IBOutlet fileprivate var restorePurchaseButton: UIButton!
   
    var dismissWithSuccessfulPurchase: (()->())?
    
    var firstSub: Subscription? {
        didSet {
            self.rightIndicatorView.stopAnimating()
            
            if let unwrappedFirstSub = firstSub {
                self.rightTitleLabel.isHidden = false
                self.rightDollarLabel.isHidden = false
                self.rightGetButton.isHidden = false
                
                self.rightTitleLabel.text = unwrappedFirstSub.product.localizedTitle
                self.rightDollarLabel.text = unwrappedFirstSub.formattedPrice
            }
        }
    }
    
    var secondSub: Subscription? {
        didSet {
            self.leftIndicatorView.stopAnimating()
            
            if let unwrappedSecondSub = secondSub {
                self.leftTitleLabel.isHidden = false
                self.leftDollarLabel.isHidden = false
                self.leftGetButton.isHidden = false

                self.leftTitleLabel.text = unwrappedSecondSub.product.localizedTitle
                self.leftDollarLabel.text = unwrappedSecondSub.formattedPrice
            }
        }
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()

        setupNotificationCenter()
        loadLayouts()
        loadSubscriptions()
    }
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        REPAnalytics.trackScreenWithName(screenName: ScreenName.UpgradeToPro, className: String(describing: self))
    }
    
    fileprivate func setupNotificationCenter() {
        NotificationCenter.default.addObserver(self,
                                               selector: #selector(handleOptionsLoaded(notification:)),
                                               name: SubscriptionService.optionsLoadedNotification,
                                               object: nil)
        NotificationCenter.default.addObserver(self,
                                               selector: #selector(handleSuccessfulPurchase(notification:)),
                                               name: SubscriptionService.purchaseSuccessfulNotification,
                                               object: nil)
        NotificationCenter.default.addObserver(self,
                                               selector: #selector(handlePurchaseIncomplete(notification:)),
                                               name: SubscriptionService.purchaseIncompleteNotification,
                                               object: nil)
    }
    
    fileprivate func loadLayouts() {
        self.headerLabel.text = L10n.learnAboutProHeader
        self.leaderTitleLabel.text = L10n.learnAboutProLeaderboard
        self.leaderTitleLabel.textColor = UIColor(named: .rePerformanceOrange)
        self.leaderDetailLabel.text = L10n.learnAboutProLeaderboardDetail
        self.friendsTitleLabel.text = L10n.learnAboutProCompareWithFriends
        self.friendsTitleLabel.textColor = UIColor(named: .rePerformanceOrange)
        self.friendsDetailLabel.text = L10n.learnAboutProCompareWithFriendsDetail
        self.dealsTitleLabel.text = L10n.learnAboutProExclusiveDeals
        self.dealsTitleLabel.textColor = UIColor(named: .rePerformanceOrange)
        self.dealsDetailLabel.text = L10n.learnAboutProExclusiveDealsDetail

        let kHeightOfHeaderAndBuffer : CGFloat = 40
      
        let kPercentageOfWidthUsedByLabel : CGFloat = 0.85

        let widthOfExclusiveLabel = kPercentageOfWidthUsedByLabel * UIScreen.main.bounds.width
      
        let boundingRect : CGSize = CGSize( width: widthOfExclusiveLabel, height : CGFloat.greatestFiniteMagnitude )
      
		let heightOfEnclosingContainer : CGFloat = NSString(string : L10n.learnAboutProExclusiveDealsDetail).boundingRect(with: boundingRect, options: NSStringDrawingOptions.usesLineFragmentOrigin, attributes: [NSAttributedString.Key.font : self.dealsDetailLabel.font], context: nil).size.height

        self.exclusiveDealsContainerViewConstraint.constant = heightOfEnclosingContainer + kHeightOfHeaderAndBuffer
   
        self.leftContainerView.addDashedBorder(strokeColor: .white, lineWidth: 1.0)
        self.rightContainerView.addDashedBorder(strokeColor: .white, lineWidth: 1.0)
        
        self.leftGetButton.setTitle(L10n.learnAboutProGet, for: .normal)
        self.leftGetButton.backgroundColor = UIColor(named: .rePerformanceOrange)
        self.rightGetButton.setTitle(L10n.learnAboutProGet, for: .normal)
        self.rightGetButton.backgroundColor = UIColor(named: .rePerformanceOrange)
        self.restorePurchaseButton.setTitle(L10n.learnAboutProRestorePurchase, for: .normal)
        self.restorePurchaseButton.backgroundColor = UIColor(named: .rePerformanceOrange)
    }
    
    fileprivate func loadSubscriptions() {
        SubscriptionService.shared.loadSubscriptionOptions()
    }
    
    @objc func handleOptionsLoaded(notification: Notification) {
        DispatchQueue.main.async { [weak self] in
            guard SubscriptionService.shared.options != nil,
               SubscriptionService.shared.options!.count > 1,
                let firstSub = SubscriptionService.shared.options?[0],
                let secondSub = SubscriptionService.shared.options?[1] else {
                self?.rightIndicatorView.stopAnimating()
                self?.leftIndicatorView.stopAnimating()
                return
            }
            self?.firstSub = firstSub
            self?.secondSub = secondSub
        }
    }

    @objc func handleSuccessfulPurchase(notification: Notification) {
        DispatchQueue.main.async { [weak self] in
            self?.setPurchaseButtonsEnabled(true)
            self?.dismissWithSuccessfulPurchase?()
        }
    }
    
    @objc func handlePurchaseIncomplete(notification: Notification) {
        DispatchQueue.main.async {
            self.setPurchaseButtonsEnabled(true)
            
            guard let message = notification.userInfo?["message"] as? String else { return }
            UIAlertController.showAlert(nil, message: message, inViewController: self)
        }
    }

    @IBAction fileprivate func leftButtonTapped(_ sender: UIButton) {
        if let unwrappedSecondSub = secondSub {
            setPurchaseButtonsEnabled(false)
            SubscriptionService.shared.purchase(subscription: unwrappedSecondSub)
        }
    }
    
    @IBAction fileprivate func rightButtonTapped(_ sender: UIButton) {
        if let unwrappedFirstSub = firstSub {
            setPurchaseButtonsEnabled(false)
            SubscriptionService.shared.purchase(subscription: unwrappedFirstSub)
        }
    }
    
    @IBAction fileprivate func restorePurchaseTapped(_ sender: UIButton) {
        setPurchaseButtonsEnabled(false)
        SubscriptionService.shared.restorePurchases()
    }
    
    fileprivate func setPurchaseButtonsEnabled(_ enabled: Bool) {
        let alpha: CGFloat = enabled ? 1.0 : 0.5
        
        self.leftGetButton.isEnabled = enabled
        self.leftGetButton.alpha = alpha
        self.rightGetButton.isEnabled = enabled
        self.rightGetButton.alpha = alpha
        self.restorePurchaseButton.isEnabled = enabled
        self.restorePurchaseButton.alpha = alpha
    }
   
    @IBAction fileprivate func termsAndConditionsButtonTapped()
    {
       let vc = StoryboardScene.Onboarding.termsAndCondVC.instantiate()
       vc.setBackgroundColor(colorToUse:  UIColor.black )
       vc.hideCloseButton()
      
       self.navigationController?.pushViewController( vc, animated: true )
    }



    @IBAction fileprivate func privacyButtonTapped()
    {
       let vc = StoryboardScene.Onboarding.termsAndCondVC.instantiate()
       vc.setBackgroundColor(colorToUse:  UIColor.black )
       vc.hideCloseButton()
       vc.setURLToLoad(url: Constants.PrivacyFilename )
      
       self.navigationController?.pushViewController( vc, animated: true )
    }
   
}
