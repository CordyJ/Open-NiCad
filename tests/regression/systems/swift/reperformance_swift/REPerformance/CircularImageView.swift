//
//  CircularImageView.swift
//  REPerformance
//
//  Created by Robert Kapizska on 2018-06-12.
//  Copyright © 2018 Push Interactions, Inc. All rights reserved.
//

import UIKit


@IBDesignable
class CircularImageView: UIImageView {
	
	private func commonInit() {
		self.layer.masksToBounds = true
		self.layer.cornerRadius = min(self.frame.size.width, self.frame.size.height) / 2
	}
	
	
	override func awakeFromNib() {
		super.awakeFromNib()
		
		self.commonInit()
	}
	
	convenience init() {
		self.init(frame: CGRect.zero)
	}
	
	override init(frame: CGRect) {
		super.init(frame: frame)
		
		self.commonInit()
	}
	
	required init?(coder aDecoder: NSCoder) {
		super.init(coder: aDecoder)
		
		self.commonInit()
	}
	
	override func prepareForInterfaceBuilder() {
		super.prepareForInterfaceBuilder()
		
		self.commonInit()
	}
	
	override func layoutSubviews() {
		super.layoutSubviews()
		
		self.layer.cornerRadius = min(self.frame.size.width, self.frame.size.height) / 2
	}
}
