
//  RewardsViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-06-07.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit
import NVActivityIndicatorView

struct SingleRewardViewData{
    let costNonMembers:String
    let costProMembers:String
    
    var itemImage:UIImage?
    var companyLogoImage:UIImage?
    
    let couponCode:String
    
    let discountDescription:String
    let productDescription:String
    
    let canRedeem:Bool
    let rightLabelText:String
    let rightViewColor:UIColor
    
    let rewardID:String
    
    let discount:Int
    let proDiscount:Int
}

struct RewardsViewData{
    var rewards:Array<SingleRewardViewData>
    let proUser:Bool
    var creditsText:String
    let upgradeToProText:String
}

class RewardsViewController: UIViewController, UITableViewDataSource, UITableViewDelegate {

    @IBOutlet var tableView:UITableView?
    
    @IBOutlet private var upgradeToProLabel:UILabel?
    @IBOutlet private var upgradeButton:UIButton?
    
    @IBOutlet weak var tableTopView: UIView!
    var creditLabel = UILabel()
    var dollarLabel = UILabel()
    
    var viewData:RewardsViewData?
    
    var rewardsWillAppear: (()->())?
    var upgrade: (()->())?
    var purchase: ((_ rewardID:String)->())?
    var viewRewardInformation: ((SingleRewardViewData)->())?

    override func viewDidLoad() {
        super.viewDidLoad()
        setUpView()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        rewardsWillAppear?()
        adjustView()
    }
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        REPAnalytics.trackScreenWithName(screenName: ScreenName.HomePage.Rewards, className: String(describing: self))
    }

    
    func setUpView(){
        tableView?.estimatedRowHeight = 206
		tableView?.rowHeight = UITableView.automaticDimension
        
        upgradeToProLabel?.textColor = UIColor.white
        
        upgradeButton?.setUpWhiteREPerformanceButton()
    }
    
    func adjustView(){
        if let viewData = self.viewData {
            upgradeToProLabel?.text = viewData.upgradeToProText
            let viewHeight:CGFloat = (viewData.proUser ? 0.0 : 119.0)
            self.tableTopView.frame.size = CGSize(width: self.tableTopView.frame.size.width, height: viewHeight)
            UIView.animate(withDuration: 0.3) {
                self.upgradeToProLabel?.isHidden = viewData.proUser
                self.upgradeButton?.isHidden = viewData.proUser
            }
        } else {
            upgradeToProLabel?.text = "Error"
            UIView.animate(withDuration: 0.3) {
                self.upgradeToProLabel?.isHidden = false
                self.upgradeButton?.isHidden = false
            }
        }
        self.creditLabel.text = String(format: "%@: %@", L10n.creditsAvailable, UserDefaults.standard.userCredits ?? 0)
        self.dollarLabel.text = String(format: "%@: $%.2f", L10n.dollarValue, UserDefaults.standard.userDollars ?? 0.00)
    }
    
    @IBAction private func upgradeTapped(_ sender:UIButton){
        upgrade?()
    }
    
    func showActivity(_ show:Bool){
        if show{
            NVActivityIndicatorPresenter.sharedInstance.startAnimating(Constants.activityData)
        } else {
            NVActivityIndicatorPresenter.sharedInstance.stopAnimating()
        }
    }
    
    //MARK: Table View
    
    func numberOfSections(in tableView: UITableView) -> Int {
        return 1
    }
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        guard let viewData = self.viewData else {
            return 0
        }
        return viewData.rewards.count
    }
    
    func tableView(_ tableView: UITableView, viewForHeaderInSection section: Int) -> UIView? {
        let headerView = UIView(frame: CGRect.init(x: 0, y: 0, width: tableView.frame.width, height: 50))
        creditLabel.frame = CGRect(x: 5, y: 5, width: headerView.frame.width - 10, height: 25)
        dollarLabel.frame = CGRect(x: 5, y:25, width: headerView.frame.width - 10, height: 25)
        headerView.backgroundColor = UIColor(named: .rePerformanceBlue)
        if let viewData = self.viewData {
            creditLabel.text = viewData.creditsText
            dollarLabel.text = String(format: "%@: %.2f", L10n.dollarValue, UserDefaults.standard.userDollars ?? 0.00)
            creditLabel.font = UIFont.systemFont(ofSize: 15.0)
            creditLabel.textColor = .white
            creditLabel.textAlignment = .center
            dollarLabel.font = UIFont.systemFont(ofSize: 15.0)
            dollarLabel.textColor = .white
            dollarLabel.textAlignment = .center
            headerView.addSubview(creditLabel)
            headerView.addSubview(dollarLabel)
        }
        
        return headerView
    }
    
    func tableView(_ tableView: UITableView, heightForHeaderInSection section: Int) -> CGFloat {
        return 50
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let defaultCell:UITableViewCell = UITableViewCell.init(style: .default, reuseIdentifier: "default")
        defaultCell.textLabel?.text = "Error"
        
        guard let viewData = self.viewData else {
            return defaultCell
        }
        
        guard let cell:RewardsTableViewCell = tableView.dequeueReusableCell(withIdentifier: Constants.Rewards.RewardsCellIdentifier, for: indexPath) as? RewardsTableViewCell else {
            return defaultCell
        }
        cell.selectionStyle = .none
        
        let cellData = viewData.rewards[indexPath.row]
        cell.configureCell(logoImage: cellData.companyLogoImage, discountDescription: cellData.discountDescription, productDescription: cellData.productDescription, percentNonMembers: cellData.discount, percentProMembers: cellData.proDiscount, dollarNonMembers: cellData.costNonMembers, dollarProMembers: cellData.costProMembers, itemImage: cellData.itemImage, rightLabelText: cellData.rightLabelText, rightViewColor: cellData.rightViewColor)
        
        return cell
        
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        if let reward = viewData?.rewards[indexPath.row]{
            if reward.canRedeem == false {
                let alertController = UIAlertController(title: L10n.purchaseAlertTitle, message: L10n.purchaseAlertMessage, preferredStyle: .alert)
                let cancelAction = UIAlertAction(title: L10n.cancel, style: .cancel, handler:nil)
                let okAction = UIAlertAction(title: L10n.ok, style: .default, handler: { (_) in
                    self.purchase?(reward.rewardID)
                })
                alertController.addAction(cancelAction)
                alertController.addAction(okAction)
                
                //https://stackoverflow.com/questions/26449724/uialertcontroller-showing-with-delay
                //http://openradar.appspot.com/19285091
                DispatchQueue.main.async {
                    self.present(alertController, animated: true, completion: nil)
                }
            } else {
                viewRewardInformation?(reward)
            }
        }
    }
    
    func reloadRow(row:Int){
        let indexPathToReload:IndexPath = IndexPath(row: row, section: 0)
        if let visibleIndexPaths = tableView?.indexPathsForVisibleRows{
            if visibleIndexPaths.contains(indexPathToReload){
                tableView?.reloadRows(at: [indexPathToReload], with: .automatic)
            }
        }
    }
}
