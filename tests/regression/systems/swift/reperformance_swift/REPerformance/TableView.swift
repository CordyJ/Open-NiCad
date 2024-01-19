//
//  TableView.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-08-16.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import UIKit


extension UITableView {
	
	func scrollToBottom(_ animated: Bool = true) {
		DispatchQueue.main.async {
			let numberOfSections = self.numberOfSections
			
			guard numberOfSections > 0 else {
				return
			}
			
			let numberOfRows = self.numberOfRows(inSection: (numberOfSections - 1))
			
			guard numberOfRows > 0 else {
				return
			}
			
			let indexPath = IndexPath(row: (numberOfRows - 1), section: (numberOfSections - 1))
			self.scrollToRow(at: indexPath, at: .bottom, animated: animated)
		}
	}
	
	func scrollToTop(_ animated: Bool = true) {
		DispatchQueue.main.async {
			let indexPath = IndexPath(row: 0, section: 0)
			self.scrollToRow(at: indexPath, at: .top, animated: animated)
		}
	}
}
