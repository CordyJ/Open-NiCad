//
//  ChallengeGymLeaderboardTableViewCell.swift
//  REPerformance
//
//  Created by Robert Kapizska on 2018-06-11.
//  Copyright © 2018 Push Interactions, Inc. All rights reserved.
//

import UIKit
import AlamofireImage


class ChallengeGymLeaderboardTableViewCell: UITableViewCell {
	
	@IBOutlet fileprivate var rankLabel: UILabel!
	@IBOutlet fileprivate var profileImageView: UIImageView!
	@IBOutlet fileprivate var nameLabel: UILabel!
	@IBOutlet fileprivate var scoreLabel: UILabel!
	@IBOutlet private var isPublicIndicatorView: UIView?
	
	
	var rank: Int? {
		didSet {
			self.rankLabel.text = "\(self.rank ?? 0)"
		}
	}
	
	var profileImageURL: URL? {
		didSet {
			if let imageURL = profileImageURL {
				self.profileImageView.af_setImage(withURL: imageURL, placeholderImage: Asset.Assets.nonFacebook.image)
			} else {
				self.profileImageView.image = Asset.Assets.nonFacebook.image
			}
		}
	}
	
	var name: String? {
		didSet {
			self.nameLabel.text = self.name
		}
	}
	
	var isPublic: Bool? {
		didSet {
			self.isPublicIndicatorView?.isHidden = ((self.isPublic ?? false) == false)
		}
	}
	
	var score: Int? {
		didSet {
			self.scoreLabel.text = "\(self.score ?? 0)"
		}
	}
	
	
	override func prepareForReuse() {
		super.prepareForReuse()
		
		self.rankLabel.text = nil
		self.nameLabel.text = nil
		self.scoreLabel.text = nil
		
		self.profileImageView.af_cancelImageRequest()
		self.profileImageView.image = nil
	}
}
