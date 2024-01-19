//
//  ExercisesReportRepsViewController.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-08.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit


class ExercisesReportRepsViewController: ExercisesReportViewController {
    
    private let repsTextFieldUpperBounds:Int = 1000
    
    @IBOutlet private var repsPerformedTextField:REPCustomTextField?
    
    override func setUpView()
    {
        super.setUpView()
        instructionsLabel?.text = L10n.exerciseWeightLiftingInputInstructions

        repsPerformedTextField?.roundCornersAndApplyBorder()
        repsPerformedTextField?.keyboardType = .numberPad
        repsPerformedTextField?.addTarget(self, action: #selector(textFieldDidChange(textField:)), for: .editingChanged)
        repsPerformedTextField?.textColor = UIColor.white
    }
    
    override func wipeView()
    {
        super.wipeView()
        repsPerformedTextField?.text = ""
    }
    
    //MARK: Text Field Changed
    @objc func textFieldDidChange(textField: REPCustomTextField){
        
        if textField == repsPerformedTextField
        {
            let sanitizedResult = textField.sanitizeIntegerInput(upperBounds: repsTextFieldUpperBounds)
            exerciseScore.reps = sanitizedResult
            
            if let sanitizedResult = sanitizedResult {
                textField.text = String(sanitizedResult)
            } else {
                textField.text = ""
            }
        }
        
        
        //Don't need to check if heart rate is nil because that input is optional from the user
        if exerciseScore.reps != nil
        {
            submitScoreButton?.setEnabled(enabled: true)
        }
        else
        {
            submitScoreButton?.setEnabled(enabled: false)
        }
    }

}
