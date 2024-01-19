//
//  OurValueTableViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-23.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class OurValueTableViewController: UIViewController, UITableViewDataSource, UITableViewDelegate {
    
    @IBOutlet private var tableView:UITableView?
    
    var viewData:Array<OurValueItem>?
    
    var endorsements: (()->())?

    override func viewDidLoad() {
        super.viewDidLoad()
        tableView?.estimatedRowHeight = 73
		tableView?.rowHeight = UITableView.automaticDimension
        tableView?.backgroundColor = UIColor.clear
        tableView?.tableFooterView = UIView()
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        REPAnalytics.trackScreenWithName(screenName: ScreenName.HomePage.OurValue, className: String(describing: self))
    }
    
    // MARK: - Table view data source

    func numberOfSections(in tableView: UITableView) -> Int {
        return 1
    }

    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        guard let count = viewData?.count else {
            return 0
        }
        return count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let defaultCell:UITableViewCell = UITableViewCell.init(style: .default, reuseIdentifier: "default")
        defaultCell.textLabel?.text = "Error"
        
        guard let viewData = self.viewData else {
            return defaultCell
        }
        
        if let endorsement:OurValueEndorsements = viewData[indexPath.row] as? OurValueEndorsements {
            guard let cell:EndorsementsTableViewCell = tableView.dequeueReusableCell(withIdentifier: Constants.OurValue.EndorsementsTableViewCellIdentifier, for: indexPath) as? EndorsementsTableViewCell else {
                return defaultCell
            }
            cell.selectionStyle = .none
            cell.setTitleLabelWithText(endorsement.question)
            return cell
        } else if let question:OurValueQuestion = viewData[indexPath.row] as? OurValueQuestion {
            guard let cell:OurValueTableViewCell = tableView.dequeueReusableCell(withIdentifier: Constants.OurValue.OurValueTableViewCellIdentifier, for: indexPath) as? OurValueTableViewCell else {
                return defaultCell
            }
            cell.selectionStyle = .none
            cell.setQuestionLabelWithText(question.question)
            cell.setAnswerLabelWithText(question.answer)
            if cell.expanded{
                cell.setAnswerLabelExpanded(true)
            } else {
                cell.setAnswerLabelExpanded(false)
            }
            return cell
        } else {
            return defaultCell
        }
        
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        
        if viewData?[indexPath.row] is OurValueEndorsements {
            endorsements?()
        } else if viewData?[indexPath.row] is OurValueQuestion {
            guard let cell:OurValueTableViewCell = tableView.cellForRow(at: indexPath) as? OurValueTableViewCell else {
                return
            }
            if cell.expanded{
                cell.setAnswerLabelExpanded(false)
                cell.rotateDisclosure(forwards: false)
            } else {
                cell.setAnswerLabelExpanded(true)
                cell.rotateDisclosure(forwards: true)
            }
            //https://stackoverflow.com/questions/460014/can-you-animate-a-height-change-on-a-uitableviewcell-when-selected
            //These two lines make the table view animate the height changes in the row. Doesn't reload data, so there is no flicker.
            tableView.beginUpdates()
            tableView.endUpdates()
        }
    }


}
