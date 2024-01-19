//
//  UIButton+Designable.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-10-04.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit


@IBDesignable
class OrangeButtonWhiteTitle: UIButton {
    
    func commonInit() {
        backgroundColor = UIColor(named: .rePerformanceOrange)
        textColor = UIColor.white
        titleLabel?.font = UIFont.boldSystemFont(ofSize: 15)
        layer.cornerRadius = Constants.UIConstants.CornerRadius
        layer.masksToBounds = true
    }
    
    override init(frame: CGRect) {
        super.init(frame: frame)
		
        commonInit()
    }
    
    required init?(coder aDecoder:NSCoder) {
        super.init(coder: aDecoder)
		
        commonInit()
    }
    
    override func prepareForInterfaceBuilder() {
        super.prepareForInterfaceBuilder()
		
        commonInit()
    }
}


@IBDesignable
class WhiteButtonYellowTitle: UIButton {
    
    func commonInit(){
        backgroundColor = UIColor.white
        textColor = UIColor(named: .rePerformanceOrange)
        titleLabel?.font = UIFont.boldSystemFont(ofSize: 15)
        layer.cornerRadius = Constants.UIConstants.CornerRadius
        layer.masksToBounds = true
    }
    
    override init(frame: CGRect){
        super.init(frame: frame)
		
        commonInit()
    }
    
    required init?(coder aDecoder:NSCoder) {
        super.init(coder: aDecoder)
		
        commonInit()
    }
    
    override func prepareForInterfaceBuilder() {
        super.prepareForInterfaceBuilder()
		
        commonInit()
    }
}


@IBDesignable
class ChangeGymBlueButton: UIButton {
    
    func commonInit() {
        backgroundColor = UIColor(named: .rePerformanceOrange)
        textColor = UIColor.white
        titleLabel?.font = UIFont.systemFont(ofSize: 17)
        layer.cornerRadius = Constants.UIConstants.CornerRadius
        layer.masksToBounds = true
    }
    
    override init(frame: CGRect) {
        super.init(frame: frame)
		
        commonInit()
    }
    
    required init?(coder aDecoder:NSCoder) {
        super.init(coder: aDecoder)
		
        commonInit()
    }
    
    override func prepareForInterfaceBuilder() {
        super.prepareForInterfaceBuilder()
		
        commonInit()
    }
}


@IBDesignable
class BlueButton: UIButton {
	
	func commonInit() {
		self.backgroundColor = UIColor(named: .rePerformanceRewardsBlue)
		self.textColor = UIColor.white
		self.titleLabel?.font = UIFont.systemFont(ofSize: 17)
		self.layer.cornerRadius = Constants.UIConstants.CornerRadius
		self.layer.masksToBounds = true
	}
	
	override init(frame: CGRect) {
		super.init(frame: frame)
		
		self.commonInit()
	}
	
	required init?(coder aDecoder:NSCoder) {
		super.init(coder: aDecoder)
		
		self.commonInit()
	}
	
	override func prepareForInterfaceBuilder() {
		super.prepareForInterfaceBuilder()
		
		self.commonInit()
	}
}
