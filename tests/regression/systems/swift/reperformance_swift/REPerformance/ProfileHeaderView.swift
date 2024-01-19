//
//  ProfileHeaderView.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-06-02.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class ProfileHeaderView: NSObject {
    
    static func getHeaderView(text:String) -> UIView{
        let titleTextFont:UIFont = UIFont.boldSystemFont(ofSize: Constants.Profile.TableViewHeaderFontSize)
        let constraintSize:CGSize = CGSize(width: UIScreen.main.bounds.width-16, height: CGFloat.greatestFiniteMagnitude)
		let labelSize: CGSize = text.boundingRect(with: constraintSize, options: .usesLineFragmentOrigin, attributes: [NSAttributedString.Key.font: titleTextFont], context: nil).size
        
        let label:UILabel = UILabel()
        label.frame = CGRect(x: 8, y: 0, width: labelSize.width, height: labelSize.height+Constants.Profile.TableViewHeaderBuffer)
        label.font = titleTextFont
        label.textColor = UIColor(named: .rePerformanceOrange)
        label.numberOfLines = 0
        label.lineBreakMode = .byWordWrapping
        label.text = text
        
        let headerView:UIView = UIView()
        headerView.addSubview(label)
        return headerView
    }
    
    static func getHeightForHeaderView(text:String) -> CGFloat{
        let titleTextFont:UIFont = UIFont.boldSystemFont(ofSize: Constants.Profile.TableViewHeaderFontSize)
        let constraintSize:CGSize = CGSize(width: UIScreen.main.bounds.width-16, height: CGFloat.greatestFiniteMagnitude)
		let labelSize: CGSize = text.boundingRect(with: constraintSize, options: .usesLineFragmentOrigin, attributes: [NSAttributedString.Key.font: titleTextFont], context: nil).size
        return labelSize.height + Constants.Profile.TableViewHeaderBuffer
    }

}
