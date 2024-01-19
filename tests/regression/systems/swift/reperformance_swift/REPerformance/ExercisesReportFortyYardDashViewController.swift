//
//  ExercisesReportFortyYardDashViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-30.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class ExercisesReportFortyYardDashViewController: ExercisesReportViewController {

    let secTextFieldUpperBounds: Int = 59
    let msTextFieldUpperBounds: Int = 99
    let averageHeartRateTextFieldUpperBounds: Int = 1000 //Unsure what heart rate upper bounds should be, accept this for now
    
    @IBOutlet private var enclosingView: UIView?
    @IBOutlet private var rightDivider: UIView?
    
    @IBOutlet private var secLabel: UILabel?
    @IBOutlet private var msLabel: UILabel?
    
    @IBOutlet var secTextField: REPCustomTextField?
    @IBOutlet var msTextField: REPCustomTextField?
    
    override func setUpView(){
        super.setUpView()
        instructionsLabel?.text = L10n.exerciseCardioInputInstructions
        
        secLabel?.textColor = UIColor.white
        msLabel?.textColor = UIColor.white
        
        secTextField?.keyboardType = .numberPad
        msTextField?.keyboardType = .numberPad
        
        secTextField?.addTarget(self, action: #selector(textFieldDidChange(textField:)), for: .editingChanged)
        msTextField?.addTarget(self, action: #selector(textFieldDidChange(textField:)), for: .editingChanged)
        
        secTextField?.textColor = UIColor.white
        msTextField?.textColor = UIColor.white
        
        enclosingView?.roundCornersAndApplyBorder()
        
        rightDivider?.backgroundColor = UIColor.init(named: .rePerformanceOrange)
    }
    
    override func wipeView() {
        super.wipeView()
        
        secTextField?.text = ""
        msTextField?.text = ""
    }
    
    //MARK: Text Field Changed
    @objc func textFieldDidChange(textField: REPCustomTextField){
        
        let upperBounds:Int = {
            if textField == self.secTextField {
                return self.secTextFieldUpperBounds
            } else if textField == self.msTextField {
                return self.msTextFieldUpperBounds
            } else {
                return 0
            }
        }()
        
        let sanitizedResult = textField.sanitizeIntegerInput(upperBounds: upperBounds)
        
        if textField == self.secTextField {
            exerciseScore.seconds = sanitizedResult
        } else if textField == self.msTextField {
            exerciseScore.milliseconds = sanitizedResult
        }
        
        if let sanitizedResult = sanitizedResult {
            textField.text = String(sanitizedResult)
        } else {
            textField.text = ""
        }
        
        
        
        //Don't need to check if heart rate is nil because that input is optional from the user
        if (exerciseScore.seconds != nil) || (exerciseScore.milliseconds != nil)
        {
            submitScoreButton?.setEnabled(enabled: true)
        }
        else
        {
            submitScoreButton?.setEnabled(enabled: false)
        }
    }

}
