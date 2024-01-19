//
//  LeaderboardDividerTableViewCell.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-26.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class LeaderboardDividerTableViewCell: UITableViewCell {
    
    @IBOutlet private var leftDot:UIView?
    @IBOutlet private var centerDot:UIView?
    @IBOutlet private var rightDot:UIView?
    
    override func awakeFromNib() {
        super.awakeFromNib()
        
        selectionStyle = .none
        
        setUpDotWithView(leftDot)
        setUpDotWithView(centerDot)
        setUpDotWithView(rightDot)
    }
    
    private func setUpDotWithView(_ view:UIView?){
        if let width:CGFloat = view?.bounds.width {
            view?.layer.cornerRadius = width/2
            view?.layer.masksToBounds = true
        }
        view?.backgroundColor = UIColor(named: .rePerformanceOrange)
    }
}
