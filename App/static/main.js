
async function getUserData(){
    const response = await fetch('/api/users');
    return response.json();
}

function loadTable(users){
    const table = document.querySelector('#result');
    for(let user of users){
        table.innerHTML += `<tr>
            <td>${user.id}</td>
            <td>${user.username}</td>
						<td>${user.email}</td>
						<td>${user.weight}</td>
	 					<td>${user.height}</td>
			 			<td>${user.age}</td>
			 			<td>${user.bio}</td>
			 			<td>${user.profile_image}</td>
        </tr>`;
    }
}

async function main(){
    const users = await getUserData();
    loadTable(users);
}

main();