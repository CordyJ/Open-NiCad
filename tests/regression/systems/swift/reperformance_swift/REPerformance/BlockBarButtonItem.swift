//
//  BlockBarButtonItem.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-08-01.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import UIKit


class BlockBarButtonItem : UIBarButtonItem {
	
	private var actionHandler: (() -> ())?
	
	convenience init(title: String?, style: UIBarButtonItem.Style, actionHandler: (() -> ())?) {
		self.init(title: title, style: style, target: nil, action: nil)
		self.target = self
		self.action = #selector(self.barButtonItemPressed(sender:))
		self.actionHandler = actionHandler
	}
	
	convenience init(barButtonSystemItem systemItem: UIBarButtonItem.SystemItem, actionHandler: (() -> ())?) {
		self.init(barButtonSystemItem: systemItem, target: nil, action: nil)
		self.target = self
		self.action = #selector(self.barButtonItemPressed(sender:))
		self.actionHandler = actionHandler
	}
	
	@objc
	private func barButtonItemPressed(sender: UIBarButtonItem) {
		if let actionHandler = self.actionHandler {
			actionHandler()
		}
	}
}
