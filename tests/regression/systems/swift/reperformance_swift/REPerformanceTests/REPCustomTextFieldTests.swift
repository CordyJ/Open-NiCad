//
//  REPCustomTextFieldTests.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-05-19.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import XCTest
@testable import REPerformance

class REPCustomTextFieldTests: XCTestCase {
    
    var repCustomTextField:REPCustomTextField = REPCustomTextField()
    
    //MARK: inputSanitization
    func testInvalidLargeInput() {
        //Given
        let bigInput:String = "200"
        repCustomTextField.text = bigInput
        
        //When
        let output = repCustomTextField.sanitizeIntegerInput(upperBounds: 59)
        
        //Then
        XCTAssertEqual(output, 20, "")
    }
    
    func testLargeInputDigitsGreaterThanUpperBoundsDigitsByTwo(){
        //Given
        let bigInput:String = "2000"
        repCustomTextField.text = bigInput
        
        //When
        let output = repCustomTextField.sanitizeIntegerInput(upperBounds: 59)
        
        //Then
        XCTAssertEqual(output, 20, "")
    }
    
    func testOutOfBoundsInputSameDigitCount(){
        //Given
        let bigInput:String = "60"
        repCustomTextField.text = bigInput
        
        //When
        let output = repCustomTextField.sanitizeIntegerInput(upperBounds: 59)
        
        //Then
        XCTAssertEqual(output, 6, "")
    }
    
    func testNegative(){
        //Given
        let bigInput:String = "-1"
        repCustomTextField.text = bigInput
        
        //When
        let output = repCustomTextField.sanitizeIntegerInput(upperBounds: 59)
        
        //Then
        XCTAssertEqual(output, 1, "")
    }
    
    func testCorrectInputIsUnchanged(){
        //Given
        let bigInput:String = "30"
        repCustomTextField.text = bigInput
        
        //When
        let output = repCustomTextField.sanitizeIntegerInput(upperBounds: 59)
        
        //Then
        XCTAssertEqual(output, 30, "")
    }
    
    func testUpperBoundsIsZero(){
        //Given
        let bigInput:String = "12"
        repCustomTextField.text = bigInput
        
        //When
        let output = repCustomTextField.sanitizeIntegerInput(upperBounds: 0)
        //Then
        XCTAssertEqual(output, 1, "Weird behaviour, your upper bounds should always be greater than 0")
    }
    
}
