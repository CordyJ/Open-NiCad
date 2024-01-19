//
//  RewardsCoordinator.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-06-07.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class RewardsCoordinator {
    
    let navigationController:UINavigationController
    let rewardsDataProvider = RewardsDataProvider()
    let rewardsViewController:RewardsViewController
    var lastUpdate:Date = Date()
    var rewardsNeedsUpdate:Bool = true
    
    init(){
        navigationController = UINavigationController()
        rewardsViewController = StoryboardScene.Rewards.rewardsVC.instantiate()
        rewardsViewController.title = L10n.rewardsTitle
        rewardsViewController.tabBarItem = UITabBarItem(title: L10n.rewardsTabItemTitle, image: #imageLiteral(resourceName: "TabBar_Rewards"), tag: 0)
        navigationController.viewControllers = [rewardsViewController]
        setUpRewardsViewController()
    }
    
    func tabBarViewController() -> UIViewController{
        return navigationController
    }
    
    func setUpRewardsViewController(){
                
        rewardsViewController.rewardsWillAppear = {
            let elapsedTimeSinceLastRetrieval = Date().timeIntervalSince(self.lastUpdate)
            if elapsedTimeSinceLastRetrieval > Constants.Rewards.RefreshTimeInterval || self.rewardsViewController.viewData?.rewards.count == 0 || self.rewardsNeedsUpdate {
                self.retreiveRewards()
            }
            var newViewData = RewardsViewData(rewards: [], proUser: SubscriptionService.shared.isActive, creditsText: self.getCreditsText(), upgradeToProText: L10n.rewardsUpgradeToProDescription)
            if let rewards = self.rewardsViewController.viewData?.rewards {
                newViewData = RewardsViewData(rewards: rewards, proUser: SubscriptionService.shared.isActive, creditsText: self.getCreditsText(), upgradeToProText: L10n.rewardsUpgradeToProDescription)
            }
            self.rewardsViewController.viewData = newViewData
            self.rewardsViewController.adjustView()
            self.updateCreditsInVC()
        }
        
        rewardsViewController.upgrade = {
            if !SubscriptionService.shared.isActive {
                let learnAboutProViewController = StoryboardScene.Leaderboard.learnAboutProVC.instantiate()

                learnAboutProViewController.title = L10n.rewardsUpgradeToProTitle
                learnAboutProViewController.navigationItem.leftBarButtonItem = UIBarButtonItem(title: L10n.doneBarItemTitle, style: .plain, target: self, action: #selector(self.dismissLearnAboutPro))
                learnAboutProViewController.dismissWithSuccessfulPurchase = { [weak self] in
                    self?.dismissLearnAboutPro()
                    self?.retreiveRewards()
                }
                
                let enclosingNav = UINavigationController(rootViewController: learnAboutProViewController)
                self.rewardsViewController.present(enclosingNav, animated: true, completion: nil)
            }
        }
        
        rewardsViewController.purchase = { rewardID in
            self.rewardsViewController.showActivity(true)
            self.rewardsDataProvider.purchaseReward(rewardID: rewardID, proUser: SubscriptionService.shared.isActive, completion: { (rewardServerFormat, errorMessage) in
                self.rewardsViewController.showActivity(false)
                self.handleSingleRewardPurchaseResponse(rewardServerFormat: rewardServerFormat, errorMessage: errorMessage)
            })
        }
        
        rewardsViewController.viewRewardInformation = { reward in
            self.moveToYourDeal(singleRewardViewData: reward)
        }
    }
    
    func moveToYourDeal(singleRewardViewData: SingleRewardViewData){
        let yourDealViewController:YourDealViewController = StoryboardScene.Rewards.yourDealVC.instantiate()
        yourDealViewController.title = L10n.yourDealTitle
        yourDealViewController.viewData = YourDealViewData(singleRewardViewData: singleRewardViewData, informationLabelText: L10n.rewardsRedeemInformation)
        
        yourDealViewController.redeem = { singleRewardViewData in
            self.moveToRedeem(singleRewardViewData: singleRewardViewData, yourDealViewController: yourDealViewController )
        }
        
        navigationController.pushViewController(yourDealViewController, animated: true)
    }
    
    func moveToRedeem(singleRewardViewData:SingleRewardViewData, yourDealViewController:YourDealViewController){
        let redeemViewController:RedeemViewController = StoryboardScene.Rewards.redeemVC.instantiate()
        redeemViewController.title = L10n.yourDealTitle
        let redeemNav = UINavigationController(rootViewController: redeemViewController)
        yourDealViewController.showActivity(true)
        
        redeemViewController.done = {
            redeemViewController.dismiss(animated: true, completion: { 
                self.navigationController.popToViewController(self.rewardsViewController, animated: true)
            })
        }
        
        self.rewardsDataProvider.redeemReward(rewardID: singleRewardViewData.rewardID, completion: { (rewardServerFormat, errorMessage) in
            yourDealViewController.showActivity(false)
            self.handleSingleRewardRedeemResponse(rewardServerFormat: rewardServerFormat, errorMessage: errorMessage, redeemViewController: redeemViewController, serverCallSuccessful: { (success) in
                yourDealViewController.present(redeemNav, animated: true, completion: nil)
            })
        })
    }
    
    func retreiveRewards(){
        rewardsViewController.showActivity(true)
        rewardsDataProvider.retreiveListOfRewards { (rewardsServerFormat, errorMessage) in
            self.rewardsViewController.showActivity(false)
            if let _ = rewardsServerFormat {
                self.rewardsNeedsUpdate = false
            }
            self.handleServerResponse(rewardsServerFormat: rewardsServerFormat, errorMessage: errorMessage)
        }
    }
    
    private func handleSingleRewardRedeemResponse(rewardServerFormat:RewardServerFormat?, errorMessage:String?, redeemViewController:RedeemViewController, serverCallSuccessful: @escaping (Bool)->()){
        if let rewardServerFormat = rewardServerFormat {
            let reward:SingleRewardViewData = getSingleRewardViewData(serverReward: rewardServerFormat)
            if let rewardsViewData = rewardsViewController.viewData?.rewards{
                for index in rewardsViewData.indices{
                    if rewardsViewData[index].rewardID == reward.rewardID{
                        rewardsViewController.viewData?.rewards[index] = reward
                        rewardsViewController.reloadRow(row: index)
                        redeemViewController.viewData = RedeemViewData(logoImage: nil, couponCode: reward.couponCode, discountDescription: reward.discountDescription, productDescription: reward.productDescription)
                        serverCallSuccessful(true)
                    }
                }
                DispatchQueue.global(qos: .userInitiated).async {
                    let images = self.loadImages(serverReward: rewardServerFormat)
                    DispatchQueue.main.async {
                        redeemViewController.viewData?.logoImage = images.companyLogoImage
                        redeemViewController.configureView()
                        for index in rewardsViewData.indices{
                            if rewardsViewData[index].rewardID == reward.rewardID{
                                self.rewardsViewController.viewData?.rewards[index].itemImage = images.itemImage
                                self.rewardsViewController.viewData?.rewards[index].companyLogoImage = images.companyLogoImage
                                self.rewardsViewController.reloadRow(row: index)
                            }
                        }
                    }
                }
            }
        } else {
            UIAlertController.showAlert(L10n.errorRedeemingReward, message: errorMessage, inViewController: self.rewardsViewController)
            serverCallSuccessful(false)
        }
        self.updateCreditsInVC()
    }
    
    private func handleSingleRewardPurchaseResponse(rewardServerFormat:RewardServerFormat?, errorMessage:String?){
        if let rewardServerFormat = rewardServerFormat {
            let reward:SingleRewardViewData = getSingleRewardViewData(serverReward: rewardServerFormat)
            if let rewardsViewData = rewardsViewController.viewData?.rewards{
                for index in rewardsViewData.indices{
                    if rewardsViewData[index].rewardID == reward.rewardID{
                        rewardsViewController.viewData?.rewards[index] = reward
                        rewardsViewController.reloadRow(row: index)
                    }
                }
                DispatchQueue.global(qos: .userInitiated).async {
                    let images = self.loadImages(serverReward: rewardServerFormat)
                    DispatchQueue.main.async {
                        for index in rewardsViewData.indices{
                            if rewardsViewData[index].rewardID == reward.rewardID{
                                self.rewardsViewController.viewData?.rewards[index].itemImage = images.itemImage
                                self.rewardsViewController.viewData?.rewards[index].companyLogoImage = images.companyLogoImage
                                self.rewardsViewController.reloadRow(row: index)
                                
                            }
                        }
                    }
                }
            }
        } else {
            UIAlertController.showAlert(L10n.errorPurchasingReward, message: errorMessage, inViewController: self.rewardsViewController)
        }
        self.updateCreditsInVC()
    }
    
    private func handleServerResponse(rewardsServerFormat:Array<RewardServerFormat>?, errorMessage:String?){
        let creditsText:String = self.getCreditsText()
        var rewardsViewData = RewardsViewData(rewards: [], proUser: SubscriptionService.shared.isActive, creditsText: creditsText, upgradeToProText: L10n.rewardsUpgradeToProDescription)
        if let rewardsServerFormat = rewardsServerFormat {
            var rewards:Array<SingleRewardViewData> = []
            for serverReward in rewardsServerFormat {
                rewards.append(getSingleRewardViewData(serverReward: serverReward))
            }
            
            rewardsViewData = RewardsViewData(rewards: rewards, proUser: SubscriptionService.shared.isActive, creditsText: creditsText, upgradeToProText: L10n.rewardsUpgradeToProDescription)
            
            DispatchQueue.global(qos: .userInitiated).async {
                for serverReward in rewardsServerFormat{
                    
                    let images = self.loadImages(serverReward: serverReward)
                    
                    DispatchQueue.main.async {
                        for index in rewardsViewData.rewards.indices{
                            if rewardsViewData.rewards[index].rewardID == serverReward.rewardID{
                                self.rewardsViewController.viewData?.rewards[index].itemImage = images.itemImage
                                self.rewardsViewController.viewData?.rewards[index].companyLogoImage = images.companyLogoImage
                                self.rewardsViewController.reloadRow(row: index)
                            }
                        }
                    }
                }
            }
            self.lastUpdate = Date()
        } else {
            UIAlertController.showAlert(L10n.errorGettingRewards, message: errorMessage, inViewController: self.rewardsViewController)
        }
        self.rewardsViewController.viewData = rewardsViewData
        self.rewardsViewController.tableView?.reloadData()
        self.updateCreditsInVC()
    }
    
    private func loadImages(serverReward:RewardServerFormat) -> (itemImage:UIImage?, companyLogoImage:UIImage?) {
        
        var itemImage:UIImage? = nil
        if let itemImageURL = serverReward.itemImageURL {
            itemImage = self.getImageWithURLString(itemImageURL)
        }
        
        var companyLogoImage:UIImage? = nil
        if let companyLogoImageURL = serverReward.logoURL {
            companyLogoImage = self.getImageWithURLString(companyLogoImageURL)
        }
        
        return (itemImage, companyLogoImage)
    }
    
    private func getSingleRewardViewData(serverReward:RewardServerFormat) -> SingleRewardViewData{
        var rightLabelText:String = L10n.rewardsGetItNow
        var rightViewColor:UIColor = UIColor(named: .rePerformanceRewardsBlue)
        if serverReward.canRedeem{
            rightLabelText = L10n.rewardsRedeem
            rightViewColor = UIColor(named: .rePerformanceRewardsOrange)
        }
        return SingleRewardViewData(costNonMembers: serverReward.costNonMembers, costProMembers: serverReward.costProMembers, itemImage: nil, companyLogoImage: nil, couponCode: serverReward.couponCode, discountDescription: serverReward.discountDescription, productDescription: serverReward.productDescription, canRedeem: serverReward.canRedeem, rightLabelText: rightLabelText, rightViewColor: rightViewColor, rewardID: serverReward.rewardID, discount: serverReward.discount, proDiscount: serverReward.proDiscount)
    }
    
    private func getImageWithURLString(_ url:String) -> UIImage?{
        if let imageURL = URL(string: url){
            do{
                let imageData =  try Data(contentsOf: imageURL)
                if let image:UIImage = UIImage(data: imageData){
                    return image
                }
            } catch {
                return nil
            }
        }
        return nil
    }


    fileprivate func getCreditsText() -> String {
        var creditsText:String = L10n.errorLoadingCredits
        if let totalCredits = UserDefaults.standard.userCredits {
            creditsText = "\(L10n.creditsAvailable): \(totalCredits)"
        }
        return creditsText
    }
    
    private func updateCreditsInVC(){
        CreditsUpdater.updateCredits { (success) in
            if success{
                self.rewardsViewController.viewData?.creditsText = self.getCreditsText()
                self.rewardsViewController.adjustView()
            }
        }
    }
    
    @IBAction func dismissLearnAboutPro() {
        rewardsViewController.dismiss(animated: true, completion: nil)
    }
    
    @IBAction func dismissYourDeal() {
        rewardsViewController.dismiss(animated: true, completion: nil)
    }
}
