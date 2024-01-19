//
//  ChatMessageTableViewCell.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-08-12.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import UIKit


class ChatMessageTableViewCell: UITableViewCell {
	
	@IBOutlet
	fileprivate var messageContentLabel: UILabel?
    @IBOutlet weak var messageImage: UIImageView!
    
	
	var messageContent: String? = nil {
		didSet {
			self.messageContentLabel?.text = self.messageContent
		}
	}
	
	
	override func prepareForReuse() {
		self.messageContent = nil
		
		super.prepareForReuse()
	}
}
