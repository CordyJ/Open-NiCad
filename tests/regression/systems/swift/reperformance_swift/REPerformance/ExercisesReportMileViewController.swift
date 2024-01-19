//
//  ExercisesReportCardioViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-09.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit

class ExercisesReportMileRunViewController: ExercisesReportFortyYardDashViewController {
    
    private let minTextFieldUpperBounds: Int = 1000
    
    @IBOutlet private var leftDivider: UIView?
    
    @IBOutlet private var minLabel: UILabel?
    
    @IBOutlet private var minTextField: REPCustomTextField?
    
    @IBOutlet var averageHeartrateTextField: REPCustomTextField?

    
    override func setUpView(){
        super.setUpView()

        minLabel?.textColor = UIColor.white

        minTextField?.keyboardType = .numberPad
        averageHeartrateTextField?.keyboardType = .numberPad
        
        minTextField?.addTarget(self, action: #selector(textFieldDidChange(textField:)), for: .editingChanged)
        averageHeartrateTextField?.addTarget(self, action: #selector(textFieldDidChange(textField:)), for: .editingChanged)
        
        minTextField?.textColor = UIColor.white
                
        averageHeartrateTextField?.roundCornersAndApplyBorder()
        
        leftDivider?.backgroundColor = UIColor.init(named: .rePerformanceOrange)
    }
    
    override func wipeView() {
        super.wipeView()
        
        minTextField?.text = ""
        averageHeartrateTextField?.text = ""
    }
    
    //MARK: Text Field Changed
    override func textFieldDidChange(textField: REPCustomTextField){
                
        let upperBounds:Int = {
            if textField == self.minTextField {
                return self.minTextFieldUpperBounds
            } else if textField == self.secTextField {
                return self.secTextFieldUpperBounds
            } else if textField == self.msTextField {
                return self.msTextFieldUpperBounds
            } else if textField == self.averageHeartrateTextField {
                return self.averageHeartRateTextFieldUpperBounds
            } else {
                return 0
            }
        }()
        
        let sanitizedResult = textField.sanitizeIntegerInput(upperBounds: upperBounds)
        
        if textField == self.minTextField {
            exerciseScore.minutes = sanitizedResult
        } else if textField == self.secTextField {
            exerciseScore.seconds = sanitizedResult
        } else if textField == self.msTextField {
            exerciseScore.milliseconds = sanitizedResult
        } else if textField == self.averageHeartrateTextField {
            exerciseScore.heartrate = sanitizedResult
        }
        
        if let sanitizedResult = sanitizedResult {
            textField.text = String(sanitizedResult)
        } else {
            textField.text = ""
        }
        
        
        
        //Don't need to check if heart rate is nil because that input is optional from the user
        if(exerciseScore.minutes != nil) || (exerciseScore.seconds != nil) || (exerciseScore.milliseconds != nil)
        {
            submitScoreButton?.setEnabled(enabled: true)
        }
        else
        {
            submitScoreButton?.setEnabled(enabled: false)
        }
    }
    
}
