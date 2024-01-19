//
//  ChatUserListViewController.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-08-12.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import UIKit
import FirebaseFirestore
import FirebaseFunctions


class ChatUserListViewController: UIViewController {
	
	@IBOutlet
	fileprivate var usersTableView: UITableView?
	
	
	deinit {
		self.snapshotListener?.remove()
	}
	
	
	var firebaseIdentifier: String? = nil {
		didSet {
			self.snapshotListener?.remove()
			
			guard let firebaseIdentifier = self.firebaseIdentifier else {
				return
			}
			
			let userConversationsReference = Firestore.firestore().collection("conversations").whereField(FieldPath(["user_ids"]), arrayContains: firebaseIdentifier)
			self.snapshotListener = userConversationsReference.addSnapshotListener() { [weak self] (snapshot, error) in
				guard let snapshot = snapshot else {
					return
				}
				
                self?.chatConversations = snapshot.documents.compactMap({ (document) in
                    let chatConversation = ChatConversation(snapshot: document)
                    // excludes empty conversation (no message date) and does a sanity check on two participants
                    if chatConversation.lastMessageDate == nil || chatConversation.participants.count < 2 {
                        return nil
                    }
                    else {
                        return chatConversation
                    }
                    // sorts by most recent first
                }).sorted{ $0.lastMessageDate! > $1.lastMessageDate! }
			}
		}
	}
	
	fileprivate var snapshotListener: ListenerRegistration?
	
	fileprivate var chatConversations: [ChatConversation]? = nil {
		didSet {
			self.usersTableView?.reloadData()
		}
	}
	
	var selectedConversation: ((ChatConversation)->())?
}


extension ChatUserListViewController: UITableViewDataSource, UITableViewDelegate {
	
	func numberOfSections(in tableView: UITableView) -> Int {
		return 1
	}
	
	func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
		guard let users = self.chatConversations else {
			return 0
		}
		
		return users.count
	}
	
	func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
		let conversation = self.chatConversations![indexPath.row]
		let cell = tableView.dequeueReusableCell(withIdentifier: "Chat User Cell Identifier", for: indexPath) as! ChatUserTableViewCell
        cell.athleteName = conversation.otherParticipant?.fullName
        cell.userProfileURL = conversation.otherParticipant?.profileURL
		cell.unreadMessagesCount = conversation.me?.unreadMessageCount ?? 0
		if let lastMessageDate = conversation.lastMessageDate {
			let timeIntervalSinceLastMessage = Date().timeIntervalSince(lastMessageDate)
			let hoursSinceLastMessage = Int(timeIntervalSinceLastMessage / 60 / 60)
			cell.lastMessageTimeInterval = L10n.hrsAgo(hoursSinceLastMessage)
		}
		else {
			cell.lastMessageTimeInterval = nil
		}
		
		return cell
	}
	
	func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
		tableView.deselectRow(at: indexPath, animated: true)
		
		let conversation = self.chatConversations![indexPath.row]
		self.selectedConversation?(conversation)
	}
}
