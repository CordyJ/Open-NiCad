//
//  ChatConversation.swift
//  REPerformance
//
//  Created by Robert Kapiszka on 2019-08-14.
//  Copyright © 2019 Push Interactions, Inc. All rights reserved.
//

import Foundation
import Firebase


struct ChatConversation {
	
	let documentIdentifier: String
	let participants: [String : ChatParticipant]
	let participantIdentifiers: [String]
	let lastMessage: String?
	let lastMessageDate: Date?
	
	var otherParticipantIdentifier: String? {
		get {
			guard let userIdentifier = UserDefaults.standard.userID else {
				return nil
			}
			
			return self.participantIdentifiers.filter({ return userIdentifier != $0 }).first
		}
	}
	
	var me: ChatParticipant? {
		get {
			guard let userIdentifier = UserDefaults.standard.userID else {
				return nil
			}
			
			return self.participants.filter({ return "\($0.key)" == userIdentifier}).first?.value
		}
	}
	
	var otherParticipant: ChatParticipant? {
		get {
			guard let otherParticipantIdentifier = self.otherParticipantIdentifier else {
				return nil
			}
			
			return self.participants.filter({ return "\($0.key)" == otherParticipantIdentifier}).first?.value
		}
	}
	
	
	init(snapshot: DocumentSnapshot) {
		let snapshotData = snapshot.data()!
		self.documentIdentifier = snapshot.documentID
		self.participantIdentifiers = snapshotData["user_ids"] as! [String]
		self.lastMessage = snapshotData["last_message_text"] as? String
		
		var participantsList = [String : ChatParticipant]()
		let participantsDictionary = (snapshotData["participants"] as! [String : [String : Any]])
		participantsDictionary.forEach({ participantsList[$0.key] = ChatParticipant(json: $0.value) })
		assert(participantsList.count == 2)
		self.participants = participantsList
		
		let timestamp = snapshotData["last_message_timestamp"] as? Timestamp
		self.lastMessageDate = timestamp?.dateValue()
	}
}


struct ChatParticipant {
	
	let firstName: String
	let lastName: String
	let unreadMessageCount: Int?
    let profileURL: String?
	
	var fullName: String {
		get {
			return "\(self.firstName) \(self.lastName)"
		}
	}
	
	
	init(json: [String : Any]) {
		self.firstName = json["first_name"] as! String
		self.lastName = json["last_name"] as! String
		self.unreadMessageCount = json["unread_count"] as? Int
        self.profileURL = json["profile_image"] as? String
	}
}


struct ChatMessage {
	
	let documentIdentifier: String
	let text: String
	let ownerIdentifier: String
	let date: Date
	
	var isOwner: Bool? {
		get {
			guard let userIdentifier = UserDefaults.standard.userID else {
				return nil
			}
			
			return self.ownerIdentifier == userIdentifier
		}
	}
	
	
	init(snapshot: DocumentSnapshot) {
		let snapshotData = snapshot.data()!
		self.documentIdentifier = snapshot.documentID
		self.text = snapshotData["text"] as! String
		self.ownerIdentifier = snapshotData["owner_id"] as! String
		
		let timestamp = snapshotData["timestamp"] as! Timestamp
		self.date = timestamp.dateValue()
	}
}
