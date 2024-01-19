//
//  ChatUserTableViewCell.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-08-12.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import UIKit
import AlamofireImage


class ChatUserTableViewCell: UITableViewCell {
	
	@IBOutlet
	fileprivate var userProfileImageView: UIImageView?
	
	@IBOutlet
	fileprivate var athleteNameLabel: UILabel?
	
	@IBOutlet
	fileprivate var lastMessageTimeIntervalLabel: UILabel?
	
	@IBOutlet
	fileprivate var unreadMessagesIndicatorView: UIView?
	
	@IBOutlet
	fileprivate var unreadMessagesCountLabel: UILabel?
	
	
	var userProfileImage: UIImage? = nil {
		didSet {
			self.userProfileImageView?.image = self.userProfileImage
		}
	}
    
    var userProfileURL: String? = nil {
        didSet {
            if let userProfileURL = userProfileURL  {
                UIImage.userProfileImage(url: URL(string:userProfileURL), completion: { (image) in
                    self.userProfileImage = image
                    })
                }
            }
    }
	
	var athleteName: String? = nil {
		didSet {
			self.athleteNameLabel?.text = self.athleteName
		}
	}
	
	var lastMessageTimeInterval: String? = nil {
		didSet {
			self.lastMessageTimeIntervalLabel?.text = self.lastMessageTimeInterval
		}
	}
	
	var unreadMessagesCount: Int = 0 {
		didSet {
			self.unreadMessagesCountLabel?.text = "\(self.unreadMessagesCount)"
			self.unreadMessagesIndicatorView?.isHidden = (self.unreadMessagesCount <= 0)
		}
	}
	
	
	override func prepareForReuse() {
		self.userProfileImage = Asset.Assets.nonFacebook.image
		self.athleteName = nil
		self.lastMessageTimeInterval = nil
		self.unreadMessagesCount = 0
		
		super.prepareForReuse()
	}
}
