//
//  UIView+Designable.swift
//  REPerformance
//
//  Created by Christopher Darc on 2017-10-03.
//  Copyright © 2017 Push Interactions, Inc. All rights reserved.
//

import UIKit


@IBDesignable
class RewardsCostView: UIView {
	
	func commonInit() {
		self.layer.borderWidth = 2.0
		self.layer.borderColor = UIColor(named: .rePerformanceRewardsGrey).cgColor
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


//https://developer.apple.com/library/content/samplecode/NavBar/Introduction/Intro.html

@IBDesignable
class ChoseLocationNavBarView: UIView {
	
	func commonInit() {}
	
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
	
	
	override func willMove(toWindow newWindow: UIWindow?) {
		super.willMove(toWindow: newWindow)
		
		self.layer.shadowOffset = CGSize(width: 0, height: (CGFloat(1) / UIScreen.main.scale))
		self.layer.shadowRadius = 0
		
		self.layer.shadowColor = #colorLiteral(red: 0, green: 0, blue: 0, alpha: 1).cgColor
		self.layer.shadowOpacity = 0.25
	}
	
	override func layoutSubviews() {
		super.layoutSubviews()
		
		let frame = bounds
		let gradient = CAGradientLayer()
		gradient.frame = frame
		gradient.colors = [UIColor(named: .rePerformanceNavGradientMiddle).cgColor, UIColor(named: .rePerformanceNavGradientEnd).cgColor]
		gradient.locations = [0.0, 1.0]
		gradient.startPoint = CGPoint(x: 0.5, y: 0.0)
		gradient.endPoint = CGPoint(x: 0.5, y: 1.0)
		self.layer.insertSublayer(gradient, at: 0)
	}
}


@IBDesignable
class DropShadowView: UIView {
	
	func commonInit() {
		self.layer.shadowColor = UIColor.lightGray.cgColor
		self.layer.shadowOffset = CGSize.zero
		self.layer.shadowOpacity = 0.7
		self.layer.shadowRadius = 4.0
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
