//
//  OurValueTableViewCell.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-23.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class OurValueTableViewCell: UITableViewCell {
    
    @IBOutlet private var questionLabel:UILabel?
    @IBOutlet private var answerLabel:UILabel?
    @IBOutlet private var disclosureImageView:UIImageView?
    
    var expanded:Bool = false
    var answerLabelText = ""

    override func awakeFromNib() {
        super.awakeFromNib()
        questionLabel?.textColor = UIColor.white
        answerLabel?.textColor = UIColor.white
        disclosureImageView?.image = Asset.Assets.disclosureIndicator.image
    }
    
    func setQuestionLabelWithText(_ text:String) {
        questionLabel?.text = text
    }
    
    func setAnswerLabelWithText(_ text:String) {
        answerLabelText = text
    }
    
    func setAnswerLabelExpanded(_ expanded:Bool){
        
        if expanded{
            self.expanded = true
            answerLabel?.text = answerLabelText
        } else {
            self.expanded = false
            answerLabel?.text = ""
        }
    }
    
    func rotateDisclosure(forwards:Bool){
        var degrees:CGFloat = 0
        if forwards{
            degrees = 180.0
        } else {
            degrees = -360.0
        }
        let radians:CGFloat = degrees * .pi/180
        UIView.animate(withDuration: 0.4) {
            self.disclosureImageView?.transform = CGAffineTransform(rotationAngle: radians)
        }
    }

}

