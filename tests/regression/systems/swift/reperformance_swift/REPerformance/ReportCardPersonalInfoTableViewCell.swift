//
//  ReportCardPersonalInfoTableViewCell.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-08-08.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import UIKit


class ReportCardPersonalInfoTableViewCell: UITableViewCell {
	
	@IBOutlet fileprivate var profileImageView: UIImageView!
	@IBOutlet fileprivate var unreadMessagesIndicatorView: UIView!
	@IBOutlet fileprivate var nameLabel: UILabel!
	@IBOutlet fileprivate var ageLabel: UILabel!
	@IBOutlet fileprivate var weightLabel: UILabel!
	@IBOutlet fileprivate var lifestyleCategoryNameLabel: UILabel!
	@IBOutlet fileprivate var shareReportButton: UIButton!
	
	@IBAction private func tappedShareReportButton(_ sender: Any) {
		self.shareReport?()
	}
	
	@IBAction private func tappedChatButton(_ sender: Any) {
		self.chat?()
	}
	
	
	var isPersonal: Bool = true {
		didSet {
			self.shareReportButton.isHidden = (self.isPersonal == false)
		}
	}
	
	var hasUnreadMessages: Bool = false {
		didSet {
			self.unreadMessagesIndicatorView.isHidden = (self.hasUnreadMessages == false)
		}
	}
	
	var profileImage: UIImage? {
		didSet {
			self.profileImageView?.image = self.profileImage
		}
	}
	
	var name: String? {
		didSet {
			self.nameLabel?.text = self.name
		}
	}
	
	var age: Int? {
		didSet {
			if let age = self.age {
				self.ageLabel?.text = "\(age)"
			}
			else {
				self.ageLabel?.text = nil
			}
		}
	}
	
	var weight: Int? {
		didSet {
			if let weight = self.weight {
				self.weightLabel?.text = "\(weight) lbs"
			}
			else {
				self.weightLabel?.text = nil
			}
		}
	}
	
	var lifestyleCategoryName: String? {
		didSet {
			self.lifestyleCategoryNameLabel?.text = self.lifestyleCategoryName
		}
	}
	
	var chat: (()->())?
	var shareReport: (()->())?
    var updateProfileImage: (()->())?
	
	
	override func awakeFromNib() {
		super.awakeFromNib()
		
		self.unreadMessagesIndicatorView?.isHidden = true
		self.profileImageView?.image = nil
		self.nameLabel?.text = nil
		self.ageLabel?.text = nil
		self.weightLabel?.text = nil
		self.lifestyleCategoryNameLabel?.text = nil
	}
    
    override func prepareForReuse() {
		self.hasUnreadMessages = false
		self.isPersonal = false
		self.profileImage = nil
		self.name = nil
		self.age = nil
		self.weight = nil
		self.lifestyleCategoryName = nil
		
		super.prepareForReuse()
	}
}
