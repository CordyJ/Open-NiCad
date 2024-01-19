<?xml version="1.0" encoding="UTF-8"?>
<definitions name="http://vcddb.konni.com" targetNamespace="urn:http://vcddb.konni.com" xmlns:typens="urn:http://vcddb.konni.com" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns="http://schemas.xmlsoap.org/wsdl/">
	<types>
		<xsd:schema xmlns="http://www.w3.org/2001/XMLSchema" targetNamespace="urn:http://vcddb.konni.com">
		<xsd:import namespace="http://schemas.xmlsoap.org/soap/encoding/"/>
 		<xsd:import namespace="http://schemas.xmlsoap.org/wsdl/"/>
 			<xsd:complexType name="ArrayOfString">
			  <xsd:complexContent>
				   <xsd:restriction base="SOAP-ENC:Array">
				    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="string[]"/>
				   </xsd:restriction>
			</xsd:complexContent>
			</xsd:complexType>
			<xsd:complexType name="ArrayOfDecimal">
			  <xsd:complexContent>
				   <xsd:restriction base="SOAP-ENC:Array">
				    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="decimal[]"/>
				   </xsd:restriction>
			</xsd:complexContent>
			</xsd:complexType>
			<xsd:complexType name="ArrayOfDateTimes">
			  <xsd:complexContent>
				   <xsd:restriction base="SOAP-ENC:Array">
				    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="dateTime[]"/>
				   </xsd:restriction>
			</xsd:complexContent>
			</xsd:complexType>
			<xsd:complexType name="vcdObj">
				<xsd:all>
					<xsd:element name="arrComments" type="typens:ArrayOfCommentObj"/>
					<xsd:element name="arrDate_added" type="typens:ArrayOfDateTimes"/>
					<xsd:element name="arrDisc_count" type="typens:ArrayOfDecimal"/>
					<xsd:element name="arrMetadata" type="typens:ArrayOfMetadataObj"/>
					<xsd:element name="arrPorncategories" type="typens:ArrayOfPorncategoryObj"/>
					<xsd:element name="arrPornstars" type="typens:ArrayOfPornstarObj"/>
					<xsd:element name="category_id" type="xsd:decimal"/>
					<xsd:element name="coversObjArr" type="typens:ArrayOfCdcoverObj"/>
					<xsd:element name="external_id" type="xsd:string"/>
					<xsd:element name="id" type="xsd:decimal"/>
					<xsd:element name="imdbObj" type="typens:imdbObj"/>
					<xsd:element name="mediaTypeObjArr" type="typens:ArrayOfMediaTypeObj"/>
					<xsd:element name="moviecategoryobj" type="typens:movieCategoryObj"/>
					<xsd:element name="ownersObjArr" type="typens:ArrayOfUserUserObj"/>
					<xsd:element name="screenshots" type="xsd:boolean"/>
					<xsd:element name="source_id" type="xsd:decimal"/>
					<xsd:element name="studio_id" type="xsd:decimal"/>
					<xsd:element name="title" type="xsd:string"/>
					<xsd:element name="year" type="xsd:decimal"/>
				</xsd:all>
			</xsd:complexType>
			<xsd:complexType name="imdbObj">
				<xsd:all>
					<xsd:element name="id" type="string"/>
					<xsd:element name="title" type="string"/>
					<xsd:element name="altTitle" type="string"/>
					<xsd:element name="image" type="string"/>
					<xsd:element name="year" type="string"/>
					<xsd:element name="plot" type="string"/>
					<xsd:element name="director" type="string"/>
					<xsd:element name="cast" type="string"/>
					<xsd:element name="rating" type="string"/>
					<xsd:element name="runtime" type="string"/>
					<xsd:element name="country" type="string"/>
					<xsd:element name="genre" type="string"/>
				</xsd:all>
			</xsd:complexType>
			<xsd:complexType name="ArrayOfVcdObj">
			  <xsd:complexContent>
				   <xsd:restriction base="SOAP-ENC:Array">
				    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="typens:vcdObj[]"/>
				   </xsd:restriction>
			</xsd:complexContent>
			</xsd:complexType>
			<xsd:complexType name="movieCategoryObj">
				<xsd:all>
					<xsd:element name="category_count" type="xsd:decimal"/>
					<xsd:element name="category_id" type="xsd:decimal"/>
					<xsd:element name="category_name" type="xsd:string"/>
				</xsd:all>
			</xsd:complexType>
			<xsd:complexType name="commentObj">
				<xsd:all>
					<xsd:element name="comment" type="xsd:string"/>
					<xsd:element name="date" type="xsd:string"/>
					<xsd:element name="id" type="xsd:decimal"/>
					<xsd:element name="isPrivate" type="xsd:boolean"/>
					<xsd:element name="owner_id" type="xsd:decimal"/>
					<xsd:element name="owner_name" type="xsd:string"/>
					<xsd:element name="vcd_id" type="xsd:decimal"/>
				</xsd:all>
			</xsd:complexType>
			<xsd:complexType name="ArrayOfCommentObj">
				  <xsd:complexContent>
				   <xsd:restriction base="SOAP-ENC:Array">
				    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="typens:commentObj[]"/>
				   </xsd:restriction>
				  </xsd:complexContent>
			</xsd:complexType>
			<xsd:complexType name="metadataObj">
				<xsd:all>
					<xsd:element name="mediatype_id" type="xsd:decimal"/>
					<xsd:element name="metadata_id" type="xsd:decimal"/>
					<xsd:element name="metadata_value" type="xsd:string"/>
					<xsd:element name="metatype_description" type="xsd:string"/>
					<xsd:element name="metatype_id" type="xsd:decimal"/>
					<xsd:element name="metatype_level" type="xsd:decimal"/>
					<xsd:element name="metatype_name" type="xsd:string"/>
					<xsd:element name="record_id" type="xsd:decimal"/>
					<xsd:element name="user_id" type="xsd:decimal"/>
				</xsd:all>
			</xsd:complexType>
			<xsd:complexType name="ArrayOfMetadataObj">
				  <xsd:complexContent>
				   <xsd:restriction base="SOAP-ENC:Array">
				    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="typens:metadataObj[]"/>
				   </xsd:restriction>
				  </xsd:complexContent>
			</xsd:complexType>
			<xsd:complexType name="porncategoryObj">
				<xsd:all>
					<xsd:element name="id" type="xsd:string"/>
					<xsd:element name="name" type="xsd:string"/>
				</xsd:all>
			</xsd:complexType>
			<xsd:complexType name="ArrayOfPorncategoryObj">
				  <xsd:complexContent>
				   <xsd:restriction base="SOAP-ENC:Array">
				    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="typens:porncategoryObj[]"/>
				   </xsd:restriction>
				  </xsd:complexContent>
			</xsd:complexType>
			<xsd:complexType name="pornstarObj">
				<xsd:all>
					<xsd:element name="biography" type="xsd:string"/>
					<xsd:element name="homepage" type="xsd:string"/>
					<xsd:element name="id" type="xsd:string"/>
					<xsd:element name="image" type="xsd:string"/>
					<xsd:element name="movie_count" type="xsd:string"/>
					<xsd:element name="movies" type="typens:ArrayOfString"/>
					<xsd:element name="name" type="xsd:string"/>
				</xsd:all>
			</xsd:complexType>
			<xsd:complexType name="ArrayOfPornstarObj">
				  <xsd:complexContent>
				   <xsd:restriction base="SOAP-ENC:Array">
				    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="typens:pornstarObj[]"/>
				   </xsd:restriction>
				  </xsd:complexContent>
			</xsd:complexType>
			<xsd:complexType name="cdcoverObj">
				<xsd:all>
					<xsd:element name="cover_id" type="xsd:decimal"/>
					<xsd:element name="covertype_id" type="xsd:decimal"/>
					<xsd:element name="coverTypeDescription" type="xsd:string"/>
					<xsd:element name="covertypeName" type="xsd:string"/>
					<xsd:element name="date_added" type="xsd:string"/>
					<xsd:element name="filename" type="xsd:string"/>
					<xsd:element name="filesize" type="xsd:double"/>
					<xsd:element name="image_id" type="xsd:decimal"/>
					<xsd:element name="owner_id" type="xsd:decimal"/>
					<xsd:element name="vcd_id" type="xsd:decimal"/>
				</xsd:all>
			</xsd:complexType>
			<xsd:complexType name="ArrayOfCdcoverObj">
				  <xsd:complexContent>
				   <xsd:restriction base="SOAP-ENC:Array">
				    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="typens:cdcoverObj[]"/>
				   </xsd:restriction>
				  </xsd:complexContent>
			</xsd:complexType>
			<xsd:complexType name="mediaTypeObj">
				<xsd:all>
					<xsd:element name="children" type="typens:ArrayOfMediaTypeObj"/>
					<xsd:element name="media_type_description" type="xsd:string"/>
					<xsd:element name="media_type_id" type="xsd:decimal"/>
					<xsd:element name="media_type_name" type="xsd:string"/>
					<xsd:element name="parent_id" type="xsd:decimal"/>
				</xsd:all>
			</xsd:complexType>
			<xsd:complexType name="ArrayOfMediaTypeObj">
				  <xsd:complexContent>
				   <xsd:restriction base="SOAP-ENC:Array">
				    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="typens:mediaTypeObj[]"/>
				   </xsd:restriction>
				  </xsd:complexContent>
			</xsd:complexType>
			<xsd:complexType name="userPropertiesObj">
				<xsd:all>
					<xsd:element name="property_description" type="xsd:string"/>
					<xsd:element name="property_id" type="xsd:decimal"/>
					<xsd:element name="property_name" type="xsd:string"/>
				</xsd:all>
			</xsd:complexType>
			<xsd:complexType name="ArrayOfUserPropertiesObj">
				  <xsd:complexContent>
				   <xsd:restriction base="SOAP-ENC:Array">
				    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="typens:userPropertiesObj[]"/>
				   </xsd:restriction>
				  </xsd:complexContent>
			</xsd:complexType>
			<xsd:complexType name="userObj">
				<xsd:all>
					<xsd:element name="dateCreated" type="xsd:dateTime"/>
					<xsd:element name="email" type="xsd:string"/>
					<xsd:element name="fullname" type="xsd:string"/>
					<xsd:element name="isDeleted" type="xsd:boolean"/>
					<xsd:element name="isDirectoryUser" type="xsd:boolean"/>
					<xsd:element name="password" type="xsd:string"/>
					<xsd:element name="role_description" type="xsd:string"/>
					<xsd:element name="role_id" type="xsd:decimal"/>
					<xsd:element name="role_name" type="xsd:string"/>
					<xsd:element name="user_id" type="xsd:decimal"/>
					<xsd:element name="username" type="xsd:string"/>
					<xsd:element name="userPropertiesArr" type="typens:ArrayOfUserPropertiesObj"/>
				</xsd:all>
			</xsd:complexType>
			<xsd:complexType name="ArrayOfUserUserObj">
				  <xsd:complexContent>
				   <xsd:restriction base="SOAP-ENC:Array">
				    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="typens:userObj[]"/>
				   </xsd:restriction>
				  </xsd:complexContent>
			</xsd:complexType>
			<xsd:complexType name="advancedSearchResults">
				<xsd:all>
					<xsd:element name="id" type="xsd:decimal"/>
					<xsd:element name="title" type="xsd:string"/>
					<xsd:element name="cat_id" type="xsd:decimal"/>
					<xsd:element name="year" type="xsd:decimal"/>
					<xsd:element name="media_id" type="xsd:decimal"/>
					<xsd:element name="rating" type="xsd:float"/>
					<xsd:element name="category" type="xsd:string"/>
					<xsd:element name="media_type" type="xsd:string"/>
				</xsd:all>
			</xsd:complexType>
			<xsd:complexType name="ArrayOfAdvancedSearchResults">
				  <xsd:complexContent>
				   <xsd:restriction base="SOAP-ENC:Array">
				    <xsd:attribute ref="SOAP-ENC:arrayType" wsdl:arrayType="typens:advancedSearchResults[]"/>
				   </xsd:restriction>
				  </xsd:complexContent>
			</xsd:complexType>
		</xsd:schema>
	</types>
	<message name="addVcd">
		<part name="obj" type="typens:vcdObj"/>
	</message>
	<message name="addVcdResponse">
		<part name="addVcdReturn" type="xsd:decimal"/>
	</message>
	<message name="addVcdToUser">
		<part name="user_id" type="xsd:decimal"/>
		<part name="vcd_id" type="xsd:decimal"/>
		<part name="mediatype" type="xsd:decimal"/>
		<part name="cds" type="xsd:decimal"/>
	</message>
	<message name="addVcdToUserResponse"/>
	<message name="advancedSearch">
		<part name="title" type="xsd:string"/>
		<part name="category" type="xsd:decimal"/>
		<part name="year" type="xsd:decimal"/>
		<part name="mediatype" type="xsd:decimal"/>
		<part name="owner" type="xsd:decimal"/>
		<part name="imdbgrade" type="xsd:float"/>
	</message>
	<message name="advancedSearchResponse">
		<part name="advancedSearchReturn" type="typens:ArrayOfAdvancedSearchResults"/>
	</message>
	<message name="crossJoin">
		<part name="user_id" type="xsd:decimal"/>
		<part name="media_id" type="xsd:decimal"/>
		<part name="category_id" type="xsd:decimal"/>
		<part name="method" type="xsd:string"/>
	</message>
	<message name="crossJoinResponse">
		<part name="crossJoinReturn" type="typens:ArrayOfVcdObj"/>
	</message>
	<message name="deleteVcdFromUser">
		<part name="vcd_id" type="xsd:decimal"/>
		<part name="media_id" type="xsd:decimal"/>
		<part name="mode" type="xsd:string"/>
		<part name="user_id" type="xsd:decimal"/>
	</message>
	<message name="deleteVcdFromUserResponse">
		<part name="deleteVcdFromUserReturn" type="xsd:boolean"/>
	</message>
	<message name="getAllVcdByUserId">
		<part name="user_id" type="xsd:decimal"/>
		<part name="simple" type="xsd:boolean"/>
	</message>
	<message name="getAllVcdByUserIdResponse">
		<part name="getAllVcdByUserIdReturn" type="typens:ArrayOfVcdObj"/>
	</message>
	<message name="getAllVcdForList">
		<part name="excluded_userid" type="xsd:decimal"/>
	</message>
	<message name="getAllVcdForListResponse">
		<part name="getAllVcdForListReturn" type="typens:ArrayOfVcdObj"/>
	</message>
	<message name="getCategoryCount">
		<part name="category_id" type="xsd:decimal"/>
		<part name="user_id" type="xsd:decimal"/>
	</message>
	<message name="getCategoryCountResponse">
		<part name="getCategoryCountReturn" type="xsd:decimal"/>
	</message>
	<message name="getCategoryCountFiltered">
		<part name="category_id" type="xsd:decimal"/>
		<part name="user_id" type="xsd:decimal"/>
	</message>
	<message name="getCategoryCountFilteredResponse">
		<part name="getCategoryCountFilteredReturn" type="xsd:decimal"/>
	</message>
	<message name="getDuplicationList"/>
	<message name="getDuplicationListResponse">
		<part name="getDuplicationListReturn" type="typens:ArrayOfString"/>
	</message>
	<message name="getLatestVcdsByUserID">
		<part name="user_id" type="xsd:decimal"/>
		<part name="count" type="xsd:decimal"/>
		<part name="simple" type="xsd:boolean"/>
	</message>
	<message name="getLatestVcdsByUserIDResponse">
		<part name="getLatestVcdsByUserIDReturn" type="typens:ArrayOfVcdObj"/>
	</message>
	<message name="getMovieCount">
		<part name="user_id" type="xsd:decimal"/>
	</message>
	<message name="getMovieCountResponse">
		<part name="getMovieCountReturn" type="xsd:decimal"/>
	</message>
	<message name="getPrintViewList">
		<part name="user_id" type="xsd:decimal"/>
		<part name="list_type" type="xsd:string"/>
	</message>
	<message name="getPrintViewListResponse">
		<part name="getPrintViewListReturn" type="typens:ArrayOfVcdObj"/>
	</message>
	<message name="getRandomMovie">
		<part name="category_id" type="xsd:decimal"/>
		<part name="use_seenlist" type="xsd:boolean"/>
	</message>
	<message name="getRandomMovieResponse">
		<part name="getRandomMovieReturn" type="typens:vcdObj"/>
	</message>
	<message name="getScreenshots">
		<part name="vcd_id" type="xsd:decimal"/>
	</message>
	<message name="getScreenshotsResponse">
		<part name="getScreenshotsReturn" type="xsd:boolean"/>
	</message>
	<message name="getSimilarMovies">
		<part name="vcd_id" type="xsd:decimal"/>
	</message>
	<message name="getSimilarMoviesResponse">
		<part name="getSimilarMoviesReturn" type="typens:ArrayOfVcdObj"/>
	</message>
	<message name="getTopTenList">
		<part name="category_id" type="xsd:decimal"/>
		<part name="arrFilter" type="typens:ArrayOfDecimal"/>
	</message>
	<message name="getTopTenListResponse">
		<part name="getTopTenListReturn" type="typens:ArrayOfVcdObj"/>
	</message>
	<message name="getVcdByAdultCategory">
		<part name="category_id" type="xsd:decimal"/>
	</message>
	<message name="getVcdByAdultCategoryResponse">
		<part name="getVcdByAdultCategoryReturn" type="typens:ArrayOfVcdObj"/>
	</message>
	<message name="getVcdByAdultStudio">
		<part name="studio_id" type="xsd:decimal"/>
	</message>
	<message name="getVcdByAdultStudioResponse">
		<part name="getVcdByAdultStudioReturn" type="typens:ArrayOfVcdObj"/>
	</message>
	<message name="getVcdByCategory">
		<part name="category_id" type="xsd:decimal"/>
		<part name="start" type="xsd:decimal"/>
		<part name="end" type="xsd:decimal"/>
		<part name="user_id" type="xsd:decimal"/>
	</message>
	<message name="getVcdByCategoryResponse">
		<part name="getVcdByCategoryReturn" type="typens:ArrayOfVcdObj"/>
	</message>
	<message name="getVcdByCategoryFiltered">
		<part name="category_id" type="xsd:decimal"/>
		<part name="start" type="xsd:decimal"/>
		<part name="end" type="xsd:decimal"/>
		<part name="user_id" type="xsd:decimal"/>
	</message>
	<message name="getVcdByCategoryFilteredResponse">
		<part name="getVcdByCategoryFilteredReturn" type="typens:ArrayOfVcdObj"/>
	</message>
	<message name="getVcdByID">
		<part name="movie_id" type="xsd:decimal"/>
	</message>
	<message name="getVcdByIDResponse">
		<part name="getVcdByIDReturn" type="typens:vcdObj"/>
	</message>
	<message name="getVcdForListByIds">
		<part name="arrIDs" type="typens:ArrayOfDecimal"/>
	</message>
	<message name="getVcdForListByIdsResponse">
		<part name="getVcdForListByIdsReturn" type="typens:ArrayOfVcdObj"/>
	</message>
	<message name="markVcdWithScreenshots">
		<part name="vcd_id" type="xsd:decimal"/>
	</message>
	<message name="markVcdWithScreenshotsResponse"/>
	<message name="search">
		<part name="keyword" type="xsd:string"/>
		<part name="method" type="xsd:string"/>
	</message>
	<message name="searchResponse">
		<part name="searchReturn" type="typens:ArrayOfVcdObj"/>
	</message>
	<message name="updateVcd">
		<part name="obj" type="typens:vcdObj"/>
	</message>
	<message name="updateVcdResponse"/>
	<message name="updateVcdInstance">
		<part name="vcd_id" type="xsd:decimal"/>
		<part name="new_mediaid" type="xsd:decimal"/>
		<part name="old_mediaid" type="xsd:decimal"/>
		<part name="new_numcds" type="xsd:decimal"/>
		<part name="oldnumcds" type="xsd:decimal"/>
	</message>
	<message name="updateVcdInstanceResponse"/>
	<portType name="MovieServicesPortType">
		<documentation>
			Provide the Web UI access to the Movie Services.
		</documentation>
		<operation name="addVcd">
			<documentation>
				Create a new movie object, returns the ID of the newly created movie object.
			</documentation>
			<input message="typens:addVcd"/>
			<output message="typens:addVcdResponse"/>
		</operation>
		<operation name="addVcdToUser">
			<documentation>
				Add a new instance of a vcd object to user.
			</documentation>
			<input message="typens:addVcdToUser"/>
			<output message="typens:addVcdToUserResponse"/>
		</operation>
		<operation name="advancedSearch">
			<documentation>
				Perform advanced search, where filters can be applied.
			</documentation>
			<input message="typens:advancedSearch"/>
			<output message="typens:advancedSearchResponse"/>
		</operation>
		<operation name="crossJoin">
			<documentation>
				Perform a cross join of movies by the logged-in user and some other Owner ID.
			</documentation>
			<input message="typens:crossJoin"/>
			<output message="typens:crossJoinResponse"/>
		</operation>
		<operation name="deleteVcdFromUser">
			<documentation>
				Remove user from the owner list of a specific movie.
			</documentation>
			<input message="typens:deleteVcdFromUser"/>
			<output message="typens:deleteVcdFromUserResponse"/>
		</operation>
		<operation name="getAllVcdByUserId">
			<documentation>
				Get all vcd objects that belong to a specific owner ID.
			</documentation>
			<input message="typens:getAllVcdByUserId"/>
			<output message="typens:getAllVcdByUserIdResponse"/>
		</operation>
		<operation name="getAllVcdForList">
			<documentation>
				Get all vcd objects for lists creations.
			</documentation>
			<input message="typens:getAllVcdForList"/>
			<output message="typens:getAllVcdForListResponse"/>
		</operation>
		<operation name="getCategoryCount">
			<documentation>
				Get count of all vcd objects that belong to a specified category.
			</documentation>
			<input message="typens:getCategoryCount"/>
			<output message="typens:getCategoryCountResponse"/>
		</operation>
		<operation name="getCategoryCountFiltered">
			<documentation>
				Get the number of movies for selected category after user filter has been applied.
			</documentation>
			<input message="typens:getCategoryCountFiltered"/>
			<output message="typens:getCategoryCountFilteredResponse"/>
		</operation>
		<operation name="getDuplicationList">
			<documentation>
				Get list of duplicate movies in the database
			</documentation>
			<input message="typens:getDuplicationList"/>
			<output message="typens:getDuplicationListResponse"/>
		</operation>
		<operation name="getLatestVcdsByUserID">
			<documentation>
				Get list of users vcd objects, ordered by creation date DESC.
			</documentation>
			<input message="typens:getLatestVcdsByUserID"/>
			<output message="typens:getLatestVcdsByUserIDResponse"/>
		</operation>
		<operation name="getMovieCount">
			<documentation>
				Get the number of movies that user owns
			</documentation>
			<input message="typens:getMovieCount"/>
			<output message="typens:getMovieCountResponse"/>
		</operation>
		<operation name="getPrintViewList">
			<documentation>
				Get all vcd objects by User ID for printview.
			</documentation>
			<input message="typens:getPrintViewList"/>
			<output message="typens:getPrintViewListResponse"/>
		</operation>
		<operation name="getRandomMovie">
			<documentation>
				Find a random vcd object, params $category_id and $use_seenlist are optional.
			</documentation>
			<input message="typens:getRandomMovie"/>
			<output message="typens:getRandomMovieResponse"/>
		</operation>
		<operation name="getScreenshots">
			<documentation>
				Check if the movie has some screenshots.
			</documentation>
			<input message="typens:getScreenshots"/>
			<output message="typens:getScreenshotsResponse"/>
		</operation>
		<operation name="getSimilarMovies">
			<documentation>
				Get similiar movies as an array of vcd objects.
			</documentation>
			<input message="typens:getSimilarMovies"/>
			<output message="typens:getSimilarMoviesResponse"/>
		</operation>
		<operation name="getTopTenList">
			<documentation>
				Get the Top Ten list of latest movies.
			</documentation>
			<input message="typens:getTopTenList"/>
			<output message="typens:getTopTenListResponse"/>
		</operation>
		<operation name="getVcdByAdultCategory">
			<documentation>
				Get vcd objects that are marked adult, and that are in a specific adult category.
			</documentation>
			<input message="typens:getVcdByAdultCategory"/>
			<output message="typens:getVcdByAdultCategoryResponse"/>
		</operation>
		<operation name="getVcdByAdultStudio">
			<documentation>
				Get all vcd objects that are linked to a specific adult studio.
			</documentation>
			<input message="typens:getVcdByAdultStudio"/>
			<output message="typens:getVcdByAdultStudioResponse"/>
		</operation>
		<operation name="getVcdByCategory">
			<documentation>
				Get all vcd objects that belong to a certain category ID.
			</documentation>
			<input message="typens:getVcdByCategory"/>
			<output message="typens:getVcdByCategoryResponse"/>
		</operation>
		<operation name="getVcdByCategoryFiltered">
			<documentation>
				Get all vcd objects that belong to a certain category ID.
			</documentation>
			<input message="typens:getVcdByCategoryFiltered"/>
			<output message="typens:getVcdByCategoryFilteredResponse"/>
		</operation>
		<operation name="getVcdByID">
			<documentation>
				Get movie by ID
			</documentation>
			<input message="typens:getVcdByID"/>
			<output message="typens:getVcdByIDResponse"/>
		</operation>
		<operation name="getVcdForListByIds">
			<documentation>
				Get specific movies by ID's.
			</documentation>
			<input message="typens:getVcdForListByIds"/>
			<output message="typens:getVcdForListByIdsResponse"/>
		</operation>
		<operation name="markVcdWithScreenshots">
			<documentation>
				Set the screenshot flag on a specified movie object.
			</documentation>
			<input message="typens:markVcdWithScreenshots"/>
			<output message="typens:markVcdWithScreenshotsResponse"/>
		</operation>
		<operation name="search">
			<documentation>
				Search the database.
			</documentation>
			<input message="typens:search"/>
			<output message="typens:searchResponse"/>
		</operation>
		<operation name="updateVcd">
			<documentation>
				Update movie
			</documentation>
			<input message="typens:updateVcd"/>
			<output message="typens:updateVcdResponse"/>
		</operation>
		<operation name="updateVcdInstance">
			<documentation>
				Update instance of a movie object, updated the media type and the cd count.
			</documentation>
			<input message="typens:updateVcdInstance"/>
			<output message="typens:updateVcdInstanceResponse"/>
		</operation>
	</portType>
	<binding name="MovieServicesBinding" type="typens:MovieServicesPortType">
		<soap:binding style="rpc" transport="http://schemas.xmlsoap.org/soap/http"/>
		<operation name="addVcd">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="addVcdToUser">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="advancedSearch">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="crossJoin">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="deleteVcdFromUser">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="getAllVcdByUserId">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="getAllVcdForList">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="getCategoryCount">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="getCategoryCountFiltered">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="getDuplicationList">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="getLatestVcdsByUserID">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="getMovieCount">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="getPrintViewList">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="getRandomMovie">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="getScreenshots">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="getSimilarMovies">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="getTopTenList">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="getVcdByAdultCategory">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="getVcdByAdultStudio">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="getVcdByCategory">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="getVcdByCategoryFiltered">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="getVcdByID">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="getVcdForListByIds">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="markVcdWithScreenshots">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="search">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="updateVcd">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
		<operation name="updateVcdInstance">
			<soap:operation soapAction="urn:MovieServicesAction"/>
			<input>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</input>
			<output>
				<soap:body namespace="urn:vcddb.konni.com" use="encoded" encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"/>
			</output>
		</operation>
	</binding>
	<service name="MovieService">
		<port name="MovieServicesPort" binding="typens:MovieServicesBinding">
			<soap:address location="http://demo.vcddb.konni.com/proxy/movie.php"/>
		</port>
	</service>
</definitions>